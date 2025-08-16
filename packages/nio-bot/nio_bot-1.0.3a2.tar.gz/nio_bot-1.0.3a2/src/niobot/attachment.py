"""
Matrix file attachments. Full e2ee support is implemented.
"""
import abc
import tempfile
import warnings

import nio
import subprocess
import json
import io
import os
import pathlib
import shutil
import magic
import typing
import enum
import aiofiles
import logging
import blurhash

from .utils import run_blocking
from .exceptions import MediaUploadException, MetadataDetectionException, MediaCodecWarning

if typing.TYPE_CHECKING:
    from .client import NioBot


log = logging.getLogger(__name__)


__all__ = (
    "detect_mime_type",
    "get_metadata_ffmpeg",
    "get_metadata_imagemagick",
    "get_metadata",
    "generate_blur_hash",
    "first_frame",
    "BaseAttachment",
    "FileAttachment",
    "ImageAttachment",
    "VideoAttachment",
    "AudioAttachment",
    "AttachmentType",
    "which",
    "SUPPORTED_CODECS",
    "SUPPORTED_VIDEO_CODECS",
    "SUPPORTED_AUDIO_CODECS",
    "SUPPORTED_IMAGE_CODECS",
)

SUPPORTED_VIDEO_CODECS = [
    "h264",
    "vp8",
    "vp9",
    "av1",
    "theora",
]
# Come on browsers, five codecs is lackluster support. I'm looking at you, Safari.
SUPPORTED_AUDIO_CODECS = [
    "speex",
    "opus",
    "aac",
    "mp3",
    "vorbis",
    "flac",
    "mp2",
]
# All of the above codecs were played in Element Desktop. A bunch were cut out, as the list was far too long.
# Realistically, I don't see the warning being useful to too many people, its literally only in to help people figure
# out why their media isn't playing.
SUPPORTED_IMAGE_CODECS = [
    "mjpeg",
    "gif",
    "png",
    "av1",
    "webp"
]
# Probably not all of them but close enough
SUPPORTED_CODECS = SUPPORTED_VIDEO_CODECS + SUPPORTED_AUDIO_CODECS + SUPPORTED_IMAGE_CODECS


def detect_mime_type(file: typing.Union[str, io.BytesIO, pathlib.Path]) -> str:
    """
    Detect the mime type of a file.

    :param file: The file to detect the mime type of. Can be a BytesIO.
    :return: The mime type of the file (e.g. `text/plain`, `image/png`, `application/pdf`, `video/webp` etc.)
    """
    if isinstance(file, str):
        file = pathlib.Path(file)

    if isinstance(file, io.BytesIO):
        current_position = file.tell()
        file.seek(0)
        mt = magic.from_buffer(file.read(), mime=True)
        file.seek(current_position)  # Reset the file position
        return mt
    elif isinstance(file, pathlib.Path):
        return magic.from_file(str(file), mime=True)
    else:
        raise TypeError("File must be a string, BytesIO, or Path object.")


def get_metadata_ffmpeg(file: typing.Union[str, pathlib.Path]) -> typing.Dict[str, typing.Any]:
    """
    Gets metadata for a file via ffprobe.

    [example output (JSON)](https://github.com/EEKIM10/niobot/raw/master/docs/assets/guides/text/example_ffprobe.json)

    :param file: The file to get metadata for. **Must be a path-like object**
    :return: A dictionary containing the metadata.
    """
    if not shutil.which("ffprobe"):
        raise FileNotFoundError("ffprobe is not installed. If it is, check your $PATH.")
    command = [
        "ffprobe",
        "-of",
        "json",
        "-loglevel",
        "9",
        "-show_format",
        "-show_streams",
        "-i",
        str(file)
    ]
    try:
        result = subprocess.run(command, capture_output=True, encoding="utf-8", errors="replace", check=True)
    except subprocess.SubprocessError as e:
        raise MetadataDetectionException("Failed to get metadata for file.", exception=e)
    log.debug("ffprobe output (%d): %s", result.returncode, result.stdout)
    data = json.loads(result.stdout or '{}')
    log.debug("parsed ffprobe output:\n%s", json.dumps(data, indent=4))
    return data


def get_metadata_imagemagick(file: pathlib.Path) -> typing.Dict[str, typing.Any]:
    """The same as `get_metadata_ffmpeg` but for ImageMagick.

    Only returns a limited subset of the data, such as one stream, which contains the format, and size,
    and the format, which contains the filename, format, and size.

    [example output (JSON)](https://github.com/EEKIM10/niobot/raw/master/docs/assets/guides/text/example_identify.json)

    :param file: The file to get metadata for. **Must be a path object**
    :return: A slimmed-down dictionary containing the metadata.
    """
    file = file.resolve(True)
    command = [
        "identify",
        str(file)
    ]
    try:
        result = subprocess.run(command, capture_output=True, encoding="utf-8", errors="replace", check=True)
    except subprocess.SubprocessError as e:
        raise MetadataDetectionException("Failed to get metadata for file.", exception=e)
    log.debug("identify output (%d): %s", result.returncode, result.stdout)
    stdout = result.stdout
    stdout = stdout[len(str(file)) + 1:]
    img_format, img_size, *_ = stdout.split()
    data = {
        "streams": [
            {
                "index": 0,
                "codec_name": img_format,
                "codec_long_name": img_format,
                "codec_type": "video",
                "height": int(img_size.split("x")[1]),
                "width": int(img_size.split("x")[0]),
            }
        ],
        "format": {
            "filename": str(file),
            "format_long_name": img_format,
            "size": str(file.stat().st_size),
        }
    }
    log.debug("Parsed identify output:\n%s", json.dumps(data, indent=4))
    return data


def get_metadata(file: typing.Union[str, pathlib.Path], mime_type: str = None) -> typing.Dict[str, typing.Any]:
    """
    Gets metadata for a file.

    This will use imagemagick (`identify`) for images where available, falling back to ffmpeg (`ffprobe`)
    for everything else.

    :param file: The file to get metadata for.
    :param mime_type: The mime type of the file. If not provided, it will be detected.
    :return: The metadata for the file. See [niobot.get_metadata_ffmpeg][] and [niobot.get_metadata_imagemagick][]
     for more information.
    """
    file = _to_path(file)
    mime = mime_type or detect_mime_type(file)
    mime = mime.split("/")[0]
    if mime == "image":
        if not shutil.which("identify"):
            log.warning(
                "Imagemagick identify not found, falling back to ffmpeg for image metadata detection. "
                "Check your $PATH."
            )
        else:
            return get_metadata_imagemagick(file)

    if mime not in ["audio", "video", "image"]:
        raise MetadataDetectionException("Unsupported mime type. Must be an audio clip, video, or image.")
    return get_metadata_ffmpeg(file)


def first_frame(file: str | pathlib.Path, file_format: str = "webp") -> bytes:
    """
    Gets the first frame of a video file.

    !!! Danger "This function creates a file on disk"
        In order to extract the frame, this function creates a temporary file on disk (or memdisk depending on where
        your tempdir is). While this file is deleted after the function is done, it is still something to be aware of.
        For example, if you're (worryingly) low on space, this function may fail to extract the frame due to a lack of
        space. Or, someone could temporarily access and read the file before it is deleted.

        This also means that this function may be slow.

    :param file: The file to get the first frame of. **Must be a path-like object**
    :param file_format: The format to save the frame as. Defaults to webp.
    :return: The first frame of the video in bytes.
    """
    if not shutil.which("ffmpeg"):
        raise FileNotFoundError("ffmpeg is not installed. If it is, check your $PATH.")
    with tempfile.NamedTemporaryFile(suffix=f".{file_format}") as f:
        command = [
            "ffmpeg",
            "-loglevel",
            "9",
            "-i",
            str(file),
            "-frames:v",
            "1",
            '-y',
            '-strict',
            '-2',
            f.name
        ]
        log.debug("Extracting first frame of %r: %s", file, ' '.join(command))
        try:
            log.debug(
                "Extraction return code: %d",
                subprocess.run(command, capture_output=True, check=True).returncode
            )
        except subprocess.SubprocessError as e:
            raise MediaUploadException("Failed to extract first frame of video.", exception=e)
        f.seek(0)
        return f.read()


def generate_blur_hash(file: str | pathlib.Path | io.BytesIO, *parts: int) -> str:
    """
    Creates a blurhash

    !!! warning "This function may be resource intensive"
        This function may be resource intensive, especially for large images. You should run this in a thread or
        process pool.

        You should also scale any images down in order to increase performance.

        See: [woltapp/blurhash](https://github.com/woltapp/blurhash)
    """
    if not parts:
        parts = 4, 3
    file = _to_path(file)
    if not isinstance(file, io.BytesIO):
        with file.open("rb") as fd:
            log.info("Generating blurhash for %s", file)
            return blurhash.encode(fd, *parts)
    else:
        log.info("Generating blurhash for BytesIO object")
        return blurhash.encode(file, *parts)


def _file_okay(file: pathlib.Path | io.BytesIO) -> typing.Literal[True]:
    """Checks if a file exists, is a file, and can be read."""
    if isinstance(file, io.BytesIO):
        if file.closed:
            raise ValueError("BytesIO object is closed.")
        if len(file.getbuffer()) == 0:
            w = ResourceWarning("BytesIO object is empty, this may cause issues. Did you mean to seek(0) first?")
            warnings.warn(w)
        return True

    if not file.exists():
        raise FileNotFoundError(f"File {file} does not exist.")
    if not file.is_file():
        raise ValueError(f"{file} is not a file.")
    if not os.access(file, os.R_OK):
        raise PermissionError(f"Cannot read {file}.")
    # Check it can have a stat() value
    file.stat()
    return True


def _to_path(file: str | pathlib.Path | io.BytesIO) -> typing.Union[pathlib.Path, io.BytesIO]:
    """Converts a string to a Path object."""
    if not isinstance(file, (str, pathlib.PurePath, io.BytesIO)):
        raise TypeError("File must be a string, BytesIO, or Path object.")

    if isinstance(file, io.BytesIO):
        return file

    if isinstance(file, str):
        file = pathlib.Path(file)
    file = file.resolve()
    return file


def _size(file: pathlib.Path | io.BytesIO) -> int:
    """Gets the size of a file."""
    if isinstance(file, io.BytesIO):
        return len(file.getbuffer())
    return file.stat().st_size


def which(file: io.BytesIO | pathlib.Path | str, mime_type: str = None) -> typing.Union[
    typing.Type["FileAttachment"],
    typing.Type["ImageAttachment"],
    typing.Type["AudioAttachment"],
    typing.Type["VideoAttachment"]
]:
    """
    Gets the correct attachment type for a file.

    This function will provide either Image/Video/Audio attachment where possible, or FileAttachment otherwise.

    For example, `image/png` (from `my_image.png`) will see `image/` and will return [`ImageAttachment`][niobot.ImageAttachment],
    and `video/mp4` (from `my_video.mp4`) will see `video/` and will return [`VideoAttachment`][niobot.VideoAttachment].

    If the mime type cannot be mapped to an attachment type, this function will return [`FileAttachment`][niobot.FileAttachment].

    ??? example "Usage"
        ```python
        import niobot
        import pathlib

        my_file = pathlib.Path("/tmp/foo.bar")
        attachment = await niobot.which(my_file).from_file(my_file)
        # or
        attachment_type = niobot.which(my_file)  # one of the BaseAttachment subclasses
        attachment = await attachment_type.from_file(my_file)
        ```

    :param file: The file or BytesIO to investigate
    :param mime_type: The optional pre-detected mime type. If this is not provided, it will be detected.
    :return: The correct type for this attachment (not instantiated)
    """
    values = {
        "image": ImageAttachment,
        "audio": AudioAttachment,
        "video": VideoAttachment,
    }
    if not mime_type:
        mime_type = detect_mime_type(file)
    mime_start = mime_type.split("/")[0].lower()
    return values.get(mime_start, FileAttachment)


class AttachmentType(enum.Enum):
    """
    Enumeration containing the different types of media.

    :var FILE: A generic file.
    :var AUDIO: An audio file.
    :var VIDEO: A video file.
    :var IMAGE: An image file.
    """
    if typing.TYPE_CHECKING:
        FILE: "AttachmentType"
        AUDIO: "AttachmentType"
        VIDEO: "AttachmentType"
        IMAGE: "AttachmentType"
    FILE = "m.file"
    AUDIO = "m.audio"
    VIDEO = "m.video"
    IMAGE = "m.image"


class BaseAttachment(abc.ABC):
    """
    Base class for attachments

    !!! note
        If you pass a custom `file_name`, this is only actually used if you pass a [io.BytesIO][] to `file`.
        If you pass a [pathlib.Path][] or a [string][str], the file name will be resolved from the path, overriding
        the `file_name` parameter.

    :param file: The file path or BytesIO object to upload.
    :param file_name: The name of the file. **Must be specified if uploading a BytesIO object.**
    :param mime_type: The mime type of the file. If not specified, it will be detected.
    :param size_bytes: The size of the file in bytes. If not specified, it will be detected.
    :param attachment_type: The type of attachment. Defaults to `AttachmentType.FILE`.

    :ivar file: The file path or BytesIO object to upload. Resolved to a [pathlib.Path][] object if a string is
    passed to `__init__`.
    :ivar file_name: The name of the file. If `file` was a string or `Path`, this will be the name of the file.
    :ivar mime_type: The mime type of the file.
    :ivar size: The size of the file in bytes.
    :ivar type: The type of attachment.
    :ivar url: The URL of the uploaded file. This is set after the file is uploaded.
    :ivar keys: The encryption keys for the file. This is set after the file is uploaded.
    """
    if typing.TYPE_CHECKING:
        file: typing.Union[pathlib.Path, io.BytesIO]
        file_name: str
        mime_type: str
        size: int
        type: AttachmentType

        url: str | None
        keys: typing.Dict[str, str] | None

    def __init__(
            self,
            file: typing.Union[str, io.BytesIO, pathlib.Path],
            file_name: str = None,
            mime_type: str = None,
            size_bytes: int = None,
            *,
            attachment_type: AttachmentType = AttachmentType.FILE
    ):
        self.file = _to_path(file)
        self.file_name = self.file.name if isinstance(self.file, pathlib.Path) else file_name
        if not self.file_name:
            raise ValueError("file_name must be specified when uploading a BytesIO object.")
        self.mime_type = mime_type or detect_mime_type(self.file)
        self.size = size_bytes or os.path.getsize(self.file)

        self.type = attachment_type
        self.url = None
        self.keys = None

    def __repr__(self):
        return "<{0.__class__.__name__} file={0.file!r} file_name={0.file_name!r} " \
               "mime_type={0.mime_type!r} size={0.size!r} type={0.type!r}>".format(self)

    def as_body(self, body: str = None) -> dict:
        """
        Generates the body for the attachment for sending. The attachment must've been uploaded first.

        :param body: The body to use (should be a textual description). Defaults to the file name.
        :return:
        """
        body = {
            "body": body or self.file_name,
            "info": {
                "mimetype": self.mime_type,
                "size": self.size,
            },
            "msgtype": self.type.value,
            "filename": self.file_name,
            "url": self.url,
        }
        if self.keys:
            body["file"] = self.keys
        return body

    @classmethod
    async def from_file(
            cls,
            file: typing.Union[str, io.BytesIO, pathlib.Path],
            file_name: str = None,
    ) -> "BaseAttachment":
        """
        Creates an attachment from a file.

        You should use this method instead of the constructor, as it will automatically detect all other values

        :param file: The file or BytesIO to attach
        :param file_name: The name of the BytesIO file, if applicable
        :return: Loaded attachment.
        """
        file = _to_path(file)
        if isinstance(file, io.BytesIO):
            if not file_name:
                raise ValueError("file_name must be specified when uploading a BytesIO object.")
        else:
            if not file_name:
                file_name = file.name

        mime_type = await run_blocking(detect_mime_type, file)
        size = _size(file)
        return cls(file, file_name, mime_type, size)

    @classmethod
    async def from_mxc(
            cls,
            client: "NioBot",
            url: str, *,
            force_write: bool | pathlib.Path = False
    ) -> "BaseAttachment":
        """
        Creates an attachment from an MXC URL.

        !!! warning "This function loads the entire attachment into memory."
            If you are downloading large attachments, you should set `force_write` to `True`, otherwise the downloaded
            attachment is pushed into an [`io.BytesIO`][] object (for speed benefits), which can cause memory issues
            on low-memory systems.

            Bear in mind that most attachments are <= 100 megabytes. Also, forcing temp file writes may not be useful
            unless your temporary file directory is backed by a physical disk, because otherwise you're just loading
            into RAM with extra steps (for example, by default, `/tmp` is in-memory on linux, but `/var/tmp` is not).

        :param client: The current client instance (used to download the attachment)
        :param url: The MXC:// url to download
        :param force_write: Whether to force writing downloaded attachments to a temporary file.
        :return: The downloaded and probed attachment.
        """
        if not hasattr(nio, "DiskDownloadResponse"):
            raise NotImplementedError("Missing required upstream change to matrix-nio. Feature unavailable.")
        if force_write is True:
            save_to = tempfile.TemporaryDirectory()  # save_to will automatically create a file
        elif force_write:
            save_to = force_write
        else:
            save_to = None
        response: nio.DiskDownloadResponse | nio.MemoryDownloadResponse = await client.download(
            url,
            save_to=save_to
        )
        if isinstance(response, nio.MemoryDownloadResponse):
            file = io.BytesIO(response.body)
        else:
            file = response.body
        return await cls.from_file(file, response.filename)

    @property
    def size_bytes(self) -> int:
        """Returns the size of this attachment in bytes."""
        return self.size

    def size_as(
            self,
            unit: typing.Literal[
                'b',
                'kb',
                'kib',
                'mb',
                'mib',
                'gb',
                'gib',
            ]
    ) -> typing.Union[int, float]:
        """
        Helper function to convert the size of this attachment into a different unit.

        ??? example "Example"
            ```python
            >>> import niobot
            >>> attachment = niobot.FileAttachment("background.png", "image/png")
            >>> attachment.size_bytes
            329945
            >>> attachment.size_as("kb")
            329.945
            >>> attachment.size_as("kib")
            322.2119140625
            >>> attachment.size_as("mb")
            0.329945
            >>> attachment.size_as("mib")
            0.31466007232666016
            ```
            *Note that due to the nature of floats, precision may be lost, especially the larger in units you go.*

        :param unit: The unit to convert into
        :return: The converted size
        """
        multi = {
            'b': 1,
            'kb': 1000,
            'kib': 1024,
            'mb': 1000 ** 2,
            'mib': 1024 ** 2,
            'gb': 1000 ** 3,
            'gib': 1024 ** 3,
        }
        return self.size_bytes / multi[unit]

    async def upload(self, client: "NioBot", encrypted: bool = False) -> "BaseAttachment":
        """
        Uploads the file to matrix.

        :param client: The client to upload
        :param encrypted: Whether to encrypt the attachment or not
        :return: The attachment
        """
        if self.keys or self.url:
            raise RuntimeError("This attachment has already been uploaded.")
        if self.file_name is None:
            if hasattr(self.file, "name"):
                self.file_name = self.file.name
            else:
                raise ValueError("file_name must be specified when uploading a BytesIO object.")
        size = self.size or _size(self.file)

        if not isinstance(self.file, io.BytesIO):
            # We can open the file async here, as this will avoid blocking the loop
            async with aiofiles.open(self.file, "rb") as f:
                result, keys = await client.upload(
                    f,
                    content_type=self.mime_type,
                    filename=self.file_name,
                    encrypt=encrypted,
                    filesize=size,
                )
        else:
            # Usually, BytesIO objects are small enough to be uploaded synchronously. Plus, they're literally just
            # in-memory.
            # For scale, here is a 1GiB BytesIO with urandom() content, seek(0)ed and read() in its entirety, with
            # timeit:
            # 47.2 ns ± 0.367 ns per loop (mean ± std. dev. of 7 runs, 10,000,000 loops each)
            # So in reality, it's not going to be a massive problem.
            result, keys = await client.upload(
                self.file,
                content_type=self.mime_type,
                filename=self.file_name,
                encrypt=encrypted,
                filesize=size,
            )
        if not isinstance(result, nio.UploadResponse):
            raise MediaUploadException("Upload failed: %r" % result, result)

        if keys:
            self.keys = keys

        self.url = result.content_uri
        return self


class SupportXYZAmorganBlurHash(BaseAttachment):
    """
    Represents an attachment that supports blurhashes.

    :param xyz_amorgan_blurhash: The blurhash of the attachment
    :ivar xyz_amorgan_blurhash: The blurhash of the attachment
    """
    if typing.TYPE_CHECKING:
        xyz_amorgan_blurhash: str

    def __init__(self, *args, xyz_amorgan_blurhash: str = None, **kwargs):
        super().__init__(*args, **kwargs)
        self.xyz_amorgan_blurhash = xyz_amorgan_blurhash

    @classmethod
    async def from_file(
            cls,
            file: typing.Union[str, io.BytesIO, pathlib.Path],
            file_name: str = None,
            xyz_amorgan_blurhash: str | bool = None,
    ) -> "SupportXYZAmorganBlurHash":
        file = _to_path(file)
        if isinstance(file, io.BytesIO):
            if not file_name:
                raise ValueError("file_name must be specified when uploading a BytesIO object.")
        else:
            if not file_name:
                file_name = file.name

        mime_type = await run_blocking(detect_mime_type, file)
        size = _size(file)
        self = cls(file, file_name, mime_type, size, xyz_amorgan_blurhash=xyz_amorgan_blurhash)
        if xyz_amorgan_blurhash is not False:
            await self.get_blurhash()
        return self

    async def get_blurhash(self, quality: typing.Tuple[int, int] = (4, 3)) -> str:
        """
        Gets the blurhash of the attachment. See: [woltapp/blurhash](https://github.com/woltapp/blurhash)

        :param quality: A tuple of the quality to generate the blurhash at. Defaults to (4, 3).
        :return: The blurhash
        """
        if isinstance(self.xyz_amorgan_blurhash, str):
            return self.xyz_amorgan_blurhash
        x = await run_blocking(generate_blur_hash, self.file)
        self.xyz_amorgan_blurhash = x
        return x

    def as_body(self, body: str = None) -> dict:
        body = super().as_body(body)
        if isinstance(self.xyz_amorgan_blurhash, str):
            body["info"]["xyz.amorgan.blurhash"] = self.xyz_amorgan_blurhash
        return body


class FileAttachment(BaseAttachment):
    """
    Represents a generic file attachment.

    You should use [VideoAttachment][niobot.attachment.VideoAttachment] for videos,
    [AudioAttachment][niobot.attachment.AudioAttachment] for audio,
    and [ImageAttachment][niobot.attachment.ImageAttachment] for images.
    This is for everything else.

    :param file: The file to upload
    :param file_name: The name of the file
    :param mime_type: The mime type of the file
    :param size_bytes: The size of the file in bytes
    """
    def __init__(
            self,
            file: typing.Union[str, io.BytesIO, pathlib.Path],
            file_name: str = None,
            mime_type: str = None,
            size_bytes: int = None,
    ):
        super().__init__(file, file_name, mime_type, size_bytes, attachment_type=AttachmentType.FILE)


class ImageAttachment(SupportXYZAmorganBlurHash):
    """
    Represents an image attachment.

    :param file: The file to upload
    :param file_name: The name of the file
    :param mime_type: The mime type of the file
    :param size_bytes: The size of the file in bytes
    :param height: The height of the image in pixels (e.g. 1080)
    :param width: The width of the image in pixels (e.g. 1920)
    :param thumbnail: A thumbnail of the image. NOT a blurhash.
    :param xyz_amorgan_blurhash: The blurhash of the image

    :ivar info: A dict of info about the image. Contains `h`, `w`, `mimetype`, and `size` keys.
    :ivar thumbnail: A thumbnail of the image. NOT a blurhash.
    """
    def __init__(
            self,
            file: typing.Union[str, io.BytesIO, pathlib.Path],
            file_name: str = None,
            mime_type: str = None,
            size_bytes: int = None,
            height: int = None,
            width: int = None,
            thumbnail: "ImageAttachment" = None,
            xyz_amorgan_blurhash: str = None,
    ):
        super().__init__(
            file,
            file_name,
            mime_type,
            size_bytes,
            xyz_amorgan_blurhash=xyz_amorgan_blurhash,
            attachment_type=AttachmentType.IMAGE
        )
        self.info = {
            "h": height,
            "w": width,
            "mimetype": mime_type,
            "size": size_bytes,
        }
        self.thumbnail = thumbnail

    @classmethod
    async def from_file(
            cls,
            file: typing.Union[str, io.BytesIO, pathlib.Path],
            file_name: str = None,
            height: int = None,
            width: int = None,
            thumbnail: "ImageAttachment" = None,
            generate_blurhash: bool = True,
            *,
            unsafe: bool = False
    ) -> "ImageAttachment":
        """
        Generates an image attachment

        :param file: The file to upload
        :param file_name: The name of the file (only used if file is a `BytesIO`)
        :param height: The height, in pixels, of this image
        :param width: The width, in pixels, of this image
        :param thumbnail: A thumbnail for this image
        :param generate_blurhash: Whether to generate a blurhash for this image
        :param unsafe: Whether to allow uploading of images with unsupported codecs. May break metadata detection.
        :return: An image attachment
        """
        file = _to_path(file)
        if isinstance(file, io.BytesIO):
            if not file_name:
                raise ValueError("file_name must be specified when uploading a BytesIO object.")
        else:
            if not file_name:
                file_name = file.name

            if height is None or width is None:
                metadata = await run_blocking(get_metadata, file)
                for stream in metadata["streams"]:
                    log.debug("Found stream in image:\n%s", stream)
                    if stream["codec_type"] == "video":
                        if stream["codec_name"].lower() not in SUPPORTED_IMAGE_CODECS and unsafe is False:
                            warning = MediaCodecWarning(stream["codec_name"], *SUPPORTED_IMAGE_CODECS)
                            warnings.warn(warning)
                        log.debug("Selecting stream %r for image", stream)
                        break
                else:
                    raise ValueError("Unable to find an image stream in the given file. Are you sure its an image?")
                # ffmpeg doesn't have an image type
                height = stream["height"]
                width = stream["width"]

        mime_type = await run_blocking(detect_mime_type, file)
        size = _size(file)
        self = cls(file, file_name, mime_type, size, height, width, thumbnail)
        if generate_blurhash:
            await self.get_blurhash()
        return self

    def as_body(self, body: str = None) -> dict:
        body = super().as_body(body)
        body["info"] = {**body["info"], **self.info}
        if self.thumbnail:
            if self.thumbnail.keys:
                body["info"]["thumbnail_file"] = self.thumbnail.keys
            body["info"]["thumbnail_info"] = self.thumbnail.info
            body["info"]["thumbnail_url"] = self.thumbnail.url
        return body


class VideoAttachment(BaseAttachment):
    """
    Represents a video attachment.

    :param file: The file to upload
    :param file_name: The name of the file
    :param mime_type: The mime type of the file
    :param size_bytes: The size of the file in bytes
    :param height: The height of the video in pixels (e.g. 1080)
    :param width: The width of the video in pixels (e.g. 1920)
    :param duration: The duration of the video in seconds
    :param thumbnail: A thumbnail of the video. NOT a blurhash.
    """
    def __init__(
            self,
            file: typing.Union[str, io.BytesIO, pathlib.Path],
            file_name: str = None,
            mime_type: str = None,
            size_bytes: int = None,
            duration: int = None,
            height: int = None,
            width: int = None,
            thumbnail: "ImageAttachment" = None,
    ):
        super().__init__(
            file,
            file_name,
            mime_type,
            size_bytes,
            attachment_type=AttachmentType.VIDEO
        )
        self.info = {
            "duration": round(duration * 1000) if duration else None,
            "h": height,
            "w": width,
            "mimetype": mime_type,
            "size": size_bytes,
        }
        self.thumbnail = thumbnail

    @classmethod
    async def from_file(
            cls,
            file: typing.Union[str, io.BytesIO, pathlib.Path],
            file_name: str = None,
            duration: int = None,
            height: int = None,
            width: int = None,
            thumbnail: ImageAttachment | typing.Literal[False] = None,
            generate_blurhash: bool = True,
    ) -> "VideoAttachment":
        """
        Generates a video attachment

        !!! warning "This function auto-generates a thumbnail!"
            As thumbnails greatly improve user experience, even with blurhashes enabled, this function will by default
            create a thumbnail of the first frame of the given video if you do not provide one yourself.
            **This may increase your initialisation time by a couple seconds, give or take!**

            If this is undesirable, pass `thumbnail=False` to disable generating a thumbnail.
            This is independent of `generate_blurhash`.

            Generated thumbnails are always WebP images, so they will always be miniature, so you shouldn't
            notice a significant increase in upload time, especially considering your video will likely be several
            megabytes.

        :param file: The file to upload
        :param file_name: The name of the file (only used if file is a `BytesIO`)
        :param duration: The duration of the video, in seconds
        :param height: The height, in pixels, of this video
        :param width: The width, in pixels, of this video
        :param thumbnail: A thumbnail for this image
        :param generate_blurhash: Whether to generate a blurhash for this image
        :return: An image attachment
        """
        file = _to_path(file)
        if isinstance(file, io.BytesIO):
            if not file_name:
                raise ValueError("file_name must be specified when uploading a BytesIO object.")
        else:
            if not file_name:
                file_name = file.name

            if height is None or width is None or duration is None:
                metadata = await run_blocking(get_metadata, file)
                for stream in metadata["streams"]:
                    if stream["codec_type"] == "video":
                        if stream["codec_name"].lower() not in SUPPORTED_VIDEO_CODECS \
                                or not stream["codec_name"].startswith("pcm_"):  # usually, pcm is supported.
                            warning = MediaCodecWarning(stream["codec_name"], *SUPPORTED_VIDEO_CODECS)
                            warnings.warn(warning)
                        height = stream["height"]
                        width = stream["width"]
                        duration = round(float(metadata["format"]["duration"]) * 1000)
                        break
                else:
                    raise ValueError("Could not find a video stream in this file.")

        mime_type = await run_blocking(detect_mime_type, file)
        size = _size(file)
        original_thumbnail = thumbnail
        if thumbnail is False:
            thumbnail = None
        self = cls(file, file_name, mime_type, size, duration, height, width, thumbnail)
        if generate_blurhash:
            if isinstance(self.thumbnail, ImageAttachment):
                await self.thumbnail.get_blurhash()
            elif isinstance(file, pathlib.Path) and original_thumbnail is not False:
                thumbnail = await run_blocking(first_frame, file)
                self.thumbnail = await ImageAttachment.from_file(io.BytesIO(thumbnail), file_name="thumbnail.webp")
        return self

    @staticmethod
    async def generate_thumbnail(video: typing.Union[str, pathlib.Path, "VideoAttachment"]) -> ImageAttachment:
        """
        Generates a thumbnail for a video.

        :param video: The video to generate a thumbnail for
        :return: The path to the generated thumbnail
        """
        if isinstance(video, VideoAttachment):
            if not isinstance(video.file, pathlib.Path):
                raise ValueError(
                    "VideoAttachment.file must be a pathlib.Path, BytesIOs are not supported for thumbnail generation"
                )
            video = video.file
        video = _to_path(video)
        x = await run_blocking(first_frame, video, "webp")
        return await ImageAttachment.from_file(io.BytesIO(x), file_name="thumbnail.webp")

    def as_body(self, body: str = None) -> dict:
        body = super().as_body(body)
        body["info"] = {**body["info"], **self.info}
        if self.thumbnail:
            if self.thumbnail.keys:
                body["info"]["thumbnail_file"] = self.thumbnail.keys
            body["info"]["thumbnail_info"] = self.thumbnail.info
            body["info"]["thumbnail_url"] = self.thumbnail.url
        return body


class AudioAttachment(BaseAttachment):
    """
    Represents an audio attachment.
    """
    def __init__(
            self,
            file: typing.Union[str, io.BytesIO, pathlib.Path],
            file_name: str = None,
            mime_type: str = None,
            size_bytes: int = None,
            duration: int = None,
    ):
        super().__init__(
            file,
            file_name,
            mime_type,
            size_bytes,
            attachment_type=AttachmentType.AUDIO
        )
        self.info = {
            "duration": round(duration * 1000) if duration else None,
            "mimetype": mime_type,
            "size": size_bytes,
        }

    @classmethod
    async def from_file(
            cls,
            file: typing.Union[str, io.BytesIO, pathlib.Path],
            file_name: str = None,
            duration: int = None,
    ) -> "AudioAttachment":
        """
        Generates an audio attachment

        :param file: The file to upload
        :param file_name: The name of the file (only used if file is a `BytesIO`)
        :param duration: The duration of the audio, in seconds
        :return: An audio attachment
        """
        file = _to_path(file)
        if isinstance(file, io.BytesIO):
            if not file_name:
                raise ValueError("file_name must be specified when uploading a BytesIO object.")
        else:
            if not file_name:
                file_name = file.name
            if duration is None:
                metadata = await run_blocking(get_metadata, file)
                duration = round(float(metadata["format"]["duration"]) * 1000)

        mime_type = await run_blocking(detect_mime_type, file)
        size = _size(file)
        self = cls(file, file_name, mime_type, size, duration)
        return self

    def as_body(self, body: str = None) -> dict:
        body = super().as_body(body)
        body["info"] = {**body["info"], **self.info}
        return body
