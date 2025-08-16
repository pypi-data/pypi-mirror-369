import functools
import inspect
import logging
import os
import types
import typing
import warnings
from collections.abc import Callable

import nio

from .context import Context
from .exceptions import (
    CheckFailure,
    CommandArgumentsError,
    CommandDisabledError,
    CommandParserError,
)

if typing.TYPE_CHECKING:
    from .client import NioBot


__all__ = ("Argument", "Command", "Module", "check", "command", "event")

_T = typing.TypeVar("_T")


class Argument:
    """Represents a command argument.

    ??? example
        ```py
        from niobot import NioBot, command, Argument

        bot = NioBot(...)

        @bot.command("echo")
        def echo(ctx: niobot.Context, message: str):
            await ctx.respond(message)

        bot.run(...)
        ```

    :param name: The name of the argument. Will be used to know which argument to pass to the command callback.
    :param arg_type: The type of the argument (e.g. str, int, etc. or a custom type)
    :param description: The description of the argument. Will be shown in the auto-generated help command.
    :param default: The default value of the argument
    :param required: Whether the argument is required or not. Defaults to True if default is ..., False otherwise.
    :param parser: A function that will parse the argument. Defaults to the default parser.
    :param greedy: When enabled, will attempt to match as many arguments as possible, without raising an error.
    If no arguments can be parsed, is merely empty, otherwise is a list of parsed arguments.
    """

    def __init__(
        self,
        name: str,
        arg_type: _T,
        *,
        description: typing.Optional[str] = None,
        default: typing.Any = ...,
        required: bool = ...,
        parser: typing.Callable[["Context", "Argument", str], typing.Optional[_T]] = ...,
        greedy: bool = False,
        raw_type: type(inspect.Parameter.POSITIONAL_OR_KEYWORD),
        **kwargs,
    ):
        if default is inspect.Parameter.default:
            default = ...
        log = logging.getLogger(__name__)
        self.name = name
        self.type = arg_type
        self.description = description
        self.default = default
        self.required = required
        if self.required is ...:
            self.required = default is ...
            self.default = None
        self.extra = kwargs
        self.parser = parser
        self.greedy = greedy
        self.raw_type = raw_type
        if self.parser is ...:
            from .utils import BUILTIN_MAPPING

            if self.type in BUILTIN_MAPPING:
                log.debug("Using builtin parser %r for %r", self.type, self)
                self.parser = BUILTIN_MAPPING[self.type]
            else:
                if self.type.__class__ is not type:
                    log.warning(
                        "Argument got an instance of a type, not a type itself: %r. Inspect as if it was its raw"
                        "type, %r.",
                        self.type,
                        type(self.type),
                    )
                    target = type(self.type)
                else:
                    target = self.type
                for base in inspect.getmro(target):
                    if base in BUILTIN_MAPPING:
                        log.debug("Using builtin parser %r for %s due to being a subclass", base, self.type)
                        self.parser = BUILTIN_MAPPING[base]
                        break
                else:
                    log.debug("Using default parser for %s", self.type)
                    self.parser = self.internal_parser
        else:
            from .utils import BUILTIN_MAPPING

            if self.parser not in BUILTIN_MAPPING:
                from .utils import Parser

                # not a basic type (such as int, str, etc.) - ensure it subclasses Parser.
                if not issubclass(type(self.parser), Parser) and not isinstance(self.parser, types.LambdaType):
                    raise TypeError(
                        "parser must be a subclass of niobot.utils.Parser, or a builtin type (e.g. str, int, etc.),"
                        "got %r" % self.parser
                    )

        if raw_type == inspect.Parameter.KEYWORD_ONLY and self.type is not str:
            raise TypeError("Keyword-only arguments must be of type str, not %r." % self.type)

    def __repr__(self):
        return (
            f"<Argument name={self.name!r} type={self.type!r} default={self.default!r} required={self.required!r} "
            f"parser={self.parser!r}>"
        )

    @staticmethod
    def internal_parser(_: Context, arg: "Argument", value: str) -> typing.Optional[_T]:
        """The default parser for the argument. Will try to convert the value to the argument type."""
        try:
            return arg.type(value)
        except ValueError:
            raise CommandParserError(f"Invalid value for argument {arg.name}: {value!r}")


class Command:
    """Represents a command.

    ??? example
        !!! note
            This example uses the `command` decorator, but you can also use the [`Command`][niobot.commands.Command]
            class directly, but you
            likely won't need to, unless you want to pass a custom command class.

            All that the `@command` decorator does is create a [`Command`][niobot.commands.Command] instance and
            add it to the bot's commands,
            while wrapping the function its decorating.

        ```py
        from niobot import NioBot, command

        bot = NioBot(...)

        @bot.command("hello")
        def hello(ctx: niobot.Context):
            await ctx.respond("Hello, %s!" % ctx.message.sender)

        bot.run(...)
        ```

    :param name: The name of the command. Will be used to invoke the command.
    :param callback: The callback to call when the command is invoked.
    :param aliases: The aliases of the command. Will also be used to invoke the command.
    :param description: The description of the command. Will be shown in the auto-generated help command.
    :param disabled:
        Whether the command is disabled or not. If disabled, the command will be hidden on the auto-generated
        help command, and will not be able to be invoked.
    :param arguments:
        A list of [`Argument`][niobot.commands.Argument] instances. Will be used to parse the arguments given to the
        command.
        `ctx` is always the first argument, regardless of what you put here.
    :param usage:
        A string representing how to use this command's arguments. Will be shown in the auto-generated help.
        Do not include the command name or your bot's prefix here, only arguments.
        For example: `usage="<message> [times]"` will show up as `[p][command] <message> [times]` in the help command.
    :param hidden:
        Whether the command is hidden or not. If hidden, the command will be always hidden on the auto-generated help.
    :param greedy:
        When enabled, `CommandArgumentsError` will not be raised if too many arguments are given to the command.
        This is useful for commands that take a variable amount of arguments, and retrieve them via `Context.args`.
    """

    def __init__(
        self,
        name: str,
        callback: Callable,
        *,
        aliases: typing.Optional[list[str]] = None,
        description: typing.Optional[str] = None,
        disabled: bool = False,
        hidden: bool = False,
        greedy: bool = False,
        usage: typing.Optional[str] = None,
        arguments: typing.Optional[list[Argument]] = None,
        **kwargs,
    ):
        self.__runtime_id = os.urandom(16).hex()
        self.log = logging.getLogger(__name__)
        self.name = name
        self.callback = callback
        self.description = description
        self.disabled = disabled
        self.aliases = aliases or []
        self.checks = kwargs.pop("checks", [])
        if hasattr(self.callback, "__nio_checks__"):
            for check_func in self.callback.__nio_checks__.keys():
                self.checks.append(check_func)
        self.hidden = hidden
        self.usage = usage or None
        self.module = kwargs.pop("module", None)
        self.arguments = arguments or None
        if not self.arguments:
            if self.arguments is False:  # do not autodetect arguments
                self.arguments = []
            else:
                self.arguments = self.autodetect_args(self.callback)
        _CTX_ARG = Argument(
            "ctx",
            Context,
            description="The context for the command",
            parser=lambda ctx, *_: ctx,
            greedy=False,
            raw_type=inspect.Parameter.POSITIONAL_OR_KEYWORD,
        )
        self.arguments.insert(0, _CTX_ARG)
        self.arguments: list[Argument]
        self.greedy = greedy

    @staticmethod
    def _get_annotation_type(
        parameter: inspect.Parameter, already_greedy: bool = False
    ) -> typing.Tuple[typing.Type, bool]:
        log = logging.getLogger(__name__).getChild("get_annotation_type")
        annotation_origin = typing.get_origin(parameter.annotation)
        annotation_args = typing.get_args(parameter.annotation)
        greedy = already_greedy

        if annotation_origin is list:  # typing.List[xyz]
            if len(annotation_args) != 1:
                raise TypeError("List types must have exactly one argument.")
            log.debug("Resolved %r to list type %r", parameter.annotation, annotation_args[0])
            argument_type = annotation_args[0]
            greedy = True
        elif annotation_origin in (typing.Union, types.UnionType):  # typing.Union[a, b] or typing.Optional[a]
            if len(annotation_args) == 2 and annotation_args[1] is type(None):
                log.debug("Resolved Union[...] (%r) to optional type %r", parameter.annotation, annotation_args[0])
                argument_type = annotation_args[0]
            else:
                raise CommandArgumentsError("Union types are not yet supported.")
        elif annotation_origin is typing.Annotated:  # typing.Annotated[real_type, real_parser]
            real_type, type_parser = annotation_args
            log.debug(
                "Resolved Annotated[...] (%r) to real type %r with parser %r",
                parameter.annotation,
                real_type,
                type_parser,
            )
            argument_type = real_type
        else:
            log.debug(
                "Assuming bare type for %r, as it has no special origin (e.g. List, Union, etc.)",
                parameter.annotation,
            )
            if not callable(parameter.annotation):
                raise TypeError(
                    f"Unsupported type annotation {parameter.annotation} for parameter {parameter.name}:"
                    f" not callable ({parameter.annotation!r}, {parameter.annotation.__class__})"
                )
            argument_type = parameter.annotation

        return argument_type, greedy

    @classmethod
    def autodetect_args(cls, callback) -> typing.List[Argument]:
        """
        Attempts to automatically detect arguments, their types, and their default values for the command,
        based on the function signature.

        This is usually quite reliable, however, also quite inflexible. If you need more control over the arguments,
        consider manually passing them to the Command constructor.

        :param callback: The function to inspect
        :return: A list of arguments. `self`, and `ctx` are skipped.
        :raises TypeError: If the parameter kind is not supported, or there was another issue with introspection.
        :raises ValueError: If there are multiple greedy arguments in the command.
        """
        log = logging.getLogger(__name__).getChild("autodetect_args")
        log.debug("Processing arguments for callback %r", callback)

        detected_arguments: typing.List[Argument] = []

        for index, parameter in enumerate(inspect.signature(callback).parameters.values()):
            if detected_arguments and detected_arguments[-1].greedy:
                raise ValueError("Cannot have arguments after a greedy argument.")
            if index == 0 and parameter.name == "self":
                log.debug("Skipping 'self' parameter at position %d", index)
                continue
            elif parameter.name in ["ctx", "context"]:
                log.debug("Skipping 'context' parameter at position %d", index)
                continue

            if parameter.kind not in (inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.KEYWORD_ONLY):
                raise TypeError(f"Unknown parameter kind {parameter.kind} is unsupported.")

            argument_type: typing.Type
            default_greedy = parameter.kind == inspect.Parameter.KEYWORD_ONLY
            if parameter.annotation is inspect.Parameter.empty:
                log.warning("No type annotation for parameter %r, assuming str", parameter)
                argument_type = str
            else:
                argument_type, default_greedy = cls._get_annotation_type(parameter, default_greedy)

            argument = Argument(
                name=parameter.name,
                arg_type=argument_type,
                default=parameter.default,
                required=parameter.default is inspect.Parameter.empty,
                raw_type=parameter.kind,
                greedy=default_greedy,
            )
            detected_arguments.append(argument)

        log.debug("Automatically detected the following arguments: %r", detected_arguments)
        return detected_arguments

    def __hash__(self):
        return hash(self.__runtime_id)

    def __eq__(self, other):
        """Checks if another command's runtime ID is the same as this one's"""
        if isinstance(other, Command):
            return self.__runtime_id == other.__runtime_id
        return False

    def __repr__(self):
        return f"<Command name={self.name!r} aliases={self.aliases} disabled={self.disabled}>"

    def __str__(self):
        return self.name

    @property
    def display_usage(self) -> str:
        """Returns the usage string for this command, auto-resolved if not pre-defined"""
        if self.usage:
            return self.usage
        usage = []
        req = "<{!s}>"
        opt = "[{!s}]"
        for arg in self.arguments[1:]:
            if arg.required:
                usage.append(req.format(arg.name))
            else:
                usage.append(opt.format(arg.name))
        return " ".join(usage)

    @staticmethod
    async def run_check(function, name: str, context: Context) -> typing.Literal[True]:
        from .utils import force_await

        try:
            cr = await force_await(function, context)
        except CheckFailure:
            raise  # re-raise existing check failures
        except Exception as e:
            raise CheckFailure(name, exception=e) from e
        if not cr:
            raise CheckFailure(name)
        return True

    async def can_run(self, ctx: Context) -> bool:
        """Checks if the current user passes all the checks on the command.

        If the user fails a check, CheckFailure is raised.
        Otherwise, True is returned.
        """
        if self.disabled:
            raise CommandDisabledError(self)

        await self.run_check(ctx.client.global_command_check, "global_command_check", ctx)
        if self.checks:
            for chk_func in self.checks:
                await self.run_check(chk_func, chk_func.__name__, ctx)
        return True

    async def parse_args(
        self,
        ctx: Context,
    ) -> typing.Dict[Argument, typing.Union[typing.Any, typing.List[typing.Any]]]:
        """Parses the arguments for the current command."""
        sentinel = os.urandom(128)  # forbid passing arguments with this failsafe
        to_pass = {}
        hit_greedy = False
        self.log.debug("Parsing arguments for command %r: %r", self, self.arguments)
        for arg in self.arguments[1:]:  # 0 is ctx
            if hit_greedy:
                raise TypeError("Got an argument after a greedy=True argument.")
            to_pass[arg] = sentinel
            if arg.greedy:
                to_pass[arg] = []
                hit_greedy = True
        next_arg = 1

        context_args = iter(ctx.args)
        for value in context_args:
            try:
                arg = self.arguments[next_arg]
            except IndexError:
                raise CommandArgumentsError(f"Too many arguments given to command {self.name}")

            self.log.debug("Parsing argument %d: %r, with value %r", next_arg, arg, value)
            try:
                parsed = arg.parser(ctx, arg, value)
                if inspect.iscoroutine(parsed):
                    parsed = await parsed
            except Exception as e:
                raise CommandParserError(f"Error while parsing argument {arg.name}: {e}") from e
            self.log.debug("Parsed argument %d (%r<%r>) to %r", next_arg, arg, value, parsed)
            if arg.greedy:
                to_pass[arg].append(parsed)
                self.log.debug("Not incrementing argument index due to greedy=True")
            else:
                to_pass[arg] = parsed
                self.log.debug("Incrementing next_arg from %d to %d", next_arg, next_arg + 1)
                next_arg += 1

        for arg, value in to_pass.items():
            if value is sentinel and arg.required:
                raise CommandArgumentsError(f"Missing required argument {arg.name}")
            if value is sentinel:
                to_pass[arg] = arg.default
            if arg.greedy and arg.raw_type == inspect.Parameter.KEYWORD_ONLY:
                to_pass[arg] = " ".join(to_pass[arg])
        return to_pass

    async def invoke(self, ctx: Context) -> typing.Coroutine:
        """Invokes the current command with the given context

        :param ctx: The current context
        :raises CommandArgumentsError: Too many/few arguments, or an error parsing an argument.
        :raises CheckFailure: A check failed
        """
        parsed_kwargs = await self.parse_args(ctx)
        parsed_args = [ctx]
        if self.module:
            parsed_args.insert(0, self.module)
        self.log.debug("Arguments to pass: %r", parsed_args)
        self.log.debug("Keyword arguments to pass: %r", parsed_kwargs)
        ctx.client.dispatch("command", ctx)
        return self.callback(*parsed_args, **{x.name: y for x, y in parsed_kwargs.items()})

    def construct_context(
        self,
        client: "NioBot",
        room: nio.MatrixRoom,
        src_event: nio.RoomMessageText,
        invoking_prefix: str,
        meta: str,
        cls: type = Context,
    ) -> Context:
        """Constructs the context for the current command.

        You will rarely need to do this, the library automatically gives you a Context when a command is run.

        :param client: The current instance of the client.
        :param room: The room the command was invoked in.
        :param src_event: The source event that triggered the command. Must be `nio.RoomMessageText`.
        :param invoking_prefix: The prefix that triggered the command.
        :param meta: The invoking string (usually the command name, however may be an alias instead)
        :param cls: The class to construct the context with. Defaults to `Context`.
        :return: The constructed Context.
        """
        if not isinstance(src_event, (nio.RoomMessageText, nio.RoomMessageNotice)):
            raise TypeError("src_event must be a textual event (i.e. m.text or m.notice).")
        return cls(client, room, src_event, self, invoking_prefix=invoking_prefix, invoking_string=meta)


def command(name: typing.Optional[str] = None, **kwargs) -> Callable:
    """Allows you to register commands later on, by loading modules.

    This differs from NioBot.command() in that commands are not automatically added, you need to load them with
    bot.mount_module
    :param name: The name of the command. Defaults to function.__name__
    :param kwargs: Any key-words to pass to Command
    :return:
    """
    cls = kwargs.pop("cls", Command)

    def decorator(func):
        nonlocal name
        name = name or func.__name__
        cmd = cls(name, func, **kwargs)
        func.__nio_command__ = cmd
        return func

    return decorator


def check(
    function: typing.Callable[[Context], typing.Union[bool, typing.Coroutine[None, None, bool]]],
) -> Callable:
    """Allows you to register checks in modules.

    ```python
    @niobot.command()
    @niobot.check(my_check_func)
    async def my_command(ctx: niobot.Context):
        pass
    ```

    :param function: The function to register as a check
    :return: The decorated function.
    """

    def decorator(command_function):
        if hasattr(command_function, "__nio_checks__"):
            command_function.__nio_checks__[function] = function.__name__
        else:
            command_function.__nio_checks__ = {function: function.__name__}
        return command_function

    decorator.internal = function
    return decorator


def event(name: typing.Optional[typing.Union[str, typing.Type[nio.Event]]] = None) -> Callable:
    """
    Allows you to register event listeners in modules.

    :param name: the name of the event (no `on_` prefix)
    :return:
    """

    def decorator(func):
        nonlocal name
        name = name or func.__name__
        func.__nio_event__ = {"function": func, "name": name, "_module_instance": None}
        return func

    return decorator


class Module:
    """Represents a module.

    A module houses a set of commands and events, and can be used to modularise your bot, and organise commands and
    their respective code into multiple files and classes for ease of use, development, and maintenance.

    :ivar bot: The bot instance this module is mounted to.
    """

    __is_nio_module__ = property(lambda _: True, doc="Indicates to niobot that this is a module")

    def __init__(self, bot: "NioBot"):
        self.bot = bot

    @property
    def client(self) -> "NioBot":
        warnings.warn(DeprecationWarning("Module.client is deprecated. Please use Module.bot instead."))
        return self.bot

    @client.setter
    def client(self, value: "NioBot"):
        self.bot = value

    def list_commands(self) -> typing.Generator[Command, None, None]:
        for _, potential_command in inspect.getmembers(self):
            if hasattr(potential_command, "__nio_command__"):
                yield potential_command.__nio_command__

    def list_events(self) -> typing.Generator[dict, None, None]:
        """Lists all the @event listeners registered in this module.

        This returns the functions themselves. You can get the event name via `result.__nio_event__["name"]`.
        """
        for _, potential_event in inspect.getmembers(self):
            if hasattr(potential_event, "__nio_event__"):
                yield potential_event.__nio_event__

    def _event_handler_callback(self, function):
        # Due to the fact events are less stateful than commands, we need to manually inject self for events
        @functools.wraps(function)
        async def wrapper(*args, **kwargs):
            return await function(self, *args, **kwargs)

        return wrapper

    def __setup__(self):
        """Setup function called once by NioBot.mount_module(). Mounts every command discovered.

        .. warning:
            If you override this function, you should ensure that you call super().__setup__() to ensure that
            commands are properly registered.
        """
        for cmd in self.list_commands():
            cmd.module = self
            logging.getLogger(__name__).debug("Discovered command %r in %s.", cmd, self.__class__.__name__)
            self.bot.add_command(cmd)

        for _event_function in self.list_events():
            _event = _event_function
            _event["_module_instance"] = self
            self.bot.add_event_listener(_event["name"], self._event_handler_callback(_event["function"]))

    def __teardown__(self):
        """Teardown function called once by NioBot.unmount_module(). Removes any command that was mounted.

        .. warning:
            If you override this function, you should ensure that you call super().__teardown__() to ensure that
            commands are properly unregistered.
        """
        for cmd in self.list_commands():
            self.bot.remove_command(cmd)
        for evnt in self.list_events():
            self.bot.remove_event_listener(evnt.__nio_event__["function"])
        del self
