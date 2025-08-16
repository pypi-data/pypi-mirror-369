import logging
import inspect
import os

import nio
import typing

from .context import Context
from .exceptions import *
from .utils import force_await, BUILTIN_MAPPING

if typing.TYPE_CHECKING:
    from .client import NioBot


__all__ = (
    "Command",
    "command",
    "event",
    "Module",
    "Argument",
    "check"
)

_T = typing.TypeVar("_T")


class Argument:
    """
    Represents a command argument.

    ??? example
        ```py
        from niobot import NioBot, command, Argument

        bot = NioBot(...)

        @bot.command("echo", arguments=[Argument("message", str)])
        def echo(ctx: niobot.Context, message: str):
            await ctx.respond(message)

        bot.run(...)
        ```

    :param name: The name of the argument. Will be used to know which argument to pass to the command callback.
    :param arg_type: The type of the argument (e.g. str, int, etc. or a custom type)
    :param description: The description of the argument. Will be shown in the auto-generated help command.
    :param default: The default value of the argument
    :param required: Whether the argument is required or not. Defaults to True if default is ..., False otherwise.
    """
    def __init__(
            self,
            name: str,
            arg_type: _T,
            *,
            description: str = None,
            default: typing.Any = ...,
            required: bool = ...,
            parser: typing.Callable[["Context", "Argument", str], typing.Optional[_T]] = ...,
            **kwargs
    ):
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
        if self.parser is ...:
            if self.type in BUILTIN_MAPPING:
                log.info("Using builtin parser %r for %s", self.type)
                self.parser = BUILTIN_MAPPING[self.type]
            else:
                for base in inspect.getmro(self.type):
                    if base in BUILTIN_MAPPING:
                        log.info("Using builtin parser %r for %s due to being a subclass", base, self.type)
                        self.parser = BUILTIN_MAPPING[base]
                        break
                else:
                    log.info("Using default parser for %s", self.type)
                    self.parser = self.internal_parser

    def __repr__(self):
        return "<Argument name={0.name!r} type={0.type!r} default={0.default!r} required={0.required!r} " \
               "parser={0.parser!r}>".format(self)

    @staticmethod
    def internal_parser(_: Context, arg: "Argument", value: str) -> typing.Optional[_T]:
        """The default parser for the argument. Will try to convert the value to the argument type."""
        try:
            return arg.type(value)
        except ValueError:
            raise CommandArgumentsError(f"Invalid value for argument {arg.name}: {value!r}")


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
    """
    _CTX_ARG = Argument(
        "ctx",
        Context,
        description="The context for the command",
        parser=lambda ctx, *_: ctx
    )

    def __init__(
            self,
            name: str,
            callback: callable,
            *,
            aliases: list[str] = None,
            description: str = None,
            disabled: bool = False,
            hidden: bool = False,
            **kwargs
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
        self.usage = kwargs.pop("usage", None)
        self.module = kwargs.pop("module", None)
        self.arguments = kwargs.pop("arguments", None)
        if not self.arguments:
            if self.arguments is False:  # do not autodetect arguments
                self.arguments = []
            else:
                self.arguments = self.autodetect_args(self.callback)
        self.arguments.insert(0, self._CTX_ARG)
        self.arguments: list[Argument]

    @staticmethod
    def autodetect_args(callback) -> list[Argument]:
        """
        Attempts to auto-detect the arguments for the command, based on the callback's signature

        :param callback: The function to inspect
        :return: A list of arguments. `self`, and `ctx` are skipped.
        """
        # We need to get each parameter's type annotation, and create an Argument for it.
        # If it has a default value, assign that default value to the Argument.
        # If the parameter is `self`, ignore it.
        # If the parameter is `ctx`, use the `Context` type.
        args = []
        for n, parameter in enumerate(inspect.signature(callback).parameters.values()):
            # If it has a parent class and this is the first parameter, skip it.
            if n == 0 and parameter.name == "self":
                continue

            if parameter.name in ["ctx", "context"] or parameter.annotation is Context:
                continue

            # Disallow *args and **kwargs
            if parameter.kind in [inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD]:
                raise CommandArgumentsError("Cannot use *args or **kwargs in command callback (argument No. %d)" % n)

            if parameter.annotation is inspect.Parameter.empty:
                a = Argument(parameter.name, str, default=parameter.default)
            else:
                a = Argument(parameter.name, parameter.annotation)

            if parameter.default is not inspect.Parameter.empty:
                a.default = parameter.default
                a.required = False
            args.append(a)
        return args

    def __hash__(self):
        return hash(self.__runtime_id)

    def __eq__(self, other):
        """Checks if another command's runtime ID is the same as this one's"""
        if isinstance(other, Command):
            return self.__runtime_id == other.__runtime_id
        else:
            return False

    def __repr__(self):
        return "<Command name={0.name!r} aliases={0.aliases} disabled={0.disabled}>".format(self)

    def __str__(self):
        return self.name

    @property
    def display_usage(self) -> str:
        """Returns the usage string for this command, auto-resolved if not pre-defined"""
        if self.usage:
            return self.usage
        else:
            usage = []
            req = "<{!s}>"
            opt = "[{!s}]"
            for arg in self.arguments[1:]:
                if arg.required:
                    usage.append(req.format(arg.name))
                else:
                    usage.append(opt.format(arg.name))
            return " ".join(usage)

    async def invoke(self, ctx: Context) -> typing.Coroutine:
        """
        Invokes the current command with the given context

        :param ctx: The current context
        :raises CommandArgumentsError: Too many/few arguments, or an error parsing an argument.
        :raises CheckFailure: A check failed
        """
        if self.checks:
            for chk_func in self.checks:
                name = self.callback.__nio_checks__[chk_func]
                try:
                    cr = await force_await(
                        chk_func,
                        ctx
                    )
                except CheckFailure:
                    raise  # re-raise existing check failures
                except Exception as e:
                    raise CheckFailure(name, exception=e) from e
                if not cr:
                    raise CheckFailure(name)

        parsed_args = []
        if len(ctx.args) > (len(self.arguments) - 1):
            raise CommandArgumentsError(f"Too many arguments given to command {self.name}")
        for index, argument in enumerate(self.arguments[1:]):
            argument: Argument

            if index >= len(ctx.args):
                if argument.required:
                    raise CommandArgumentsError(f"Missing required argument {argument.name}")
                else:
                    parsed_args.append(argument.default)
                    continue

            self.log.debug("Resolved argument %s to %r", argument.name, ctx.args[index])
            try:
                parsed_argument = await force_await(
                    argument.parser,
                    ctx, 
                    argument, 
                    ctx.args[index]
                )
            except Exception as e:
                error = f"Error while parsing argument {argument.name}: {e}"
                raise CommandArgumentsError(error) from e
            parsed_args.append(parsed_argument)

        parsed_args = [ctx, *parsed_args]
        self.log.debug("Arguments to pass: %r", parsed_args)
        if self.module:
            self.log.debug("Will pass module instance")
            return self.callback(self.module, *parsed_args)
        else:
            return self.callback(*parsed_args)

    def construct_context(
            self,
            client: "NioBot",
            room: nio.MatrixRoom,
            src_event: nio.RoomMessageText,
            meta: str
    ) -> Context:
        return Context(client, room, src_event, self, invoking_string=meta)


def command(name: str = None, **kwargs) -> callable:
    """
    Allows you to register commands later on, by loading modules.

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
        name: str = None,
) -> callable:
    """
    Allows you to register checks in modules.

    ```python
    @niobot.command()
    @niobot.check(my_check_func, name="My Check")
    async def my_command(ctx: niobot.Context):
        pass
    ```

    :param function: The function to register as a check
    :param name: A human-readable name for the check. Defaults to function.__name__
    :return: The decorated function.
=    """
    def decorator(command_function):
        if hasattr(command_function, "__nio_checks__"):
            command_function.__nio_checks__[function] = name or function.__name__
        else:
            command_function.__nio_checks__ = {
                function: name or function.__name__
            }
        return command_function

    decorator.internal = function
    return decorator


def event(name: str) -> callable:
    """
    Allows you to register event listeners in modules.

    :param name: the name of the event (no ``on_`` prefix)
    :return:
    """
    def decorator(func):
        func.__nio_event__ = {
            "function": func,
            "name": name,
            "_module_instance": None
        }
        return func
    return decorator


class Module:
    __is_nio_module__ = True

    def __init__(self, bot: "NioBot"):
        self.bot = self.client = bot
        self.log = logging.getLogger(__name__)

    def list_commands(self):
        for _, potential_command in inspect.getmembers(self):
            if hasattr(potential_command, "__nio_command__"):
                yield potential_command.__nio_command__

    def list_events(self):
        for _, potential_event in inspect.getmembers(self):
            if hasattr(potential_event, "__nio_event__"):
                yield potential_event.__nio_event__

    def _event_handler_callback(self, function):
        # Due to the fact events are less stateful than commands, we need to manually inject self for events
        async def wrapper(*args, **kwargs):
            return await function(self, *args, **kwargs)
        return wrapper

    def __setup__(self):
        """Setup function called once by NioBot.mount_module(). Mounts every command discovered."""
        for cmd in self.list_commands():
            cmd.module = self
            logging.getLogger(__name__).info("Discovered command %r in %s.", cmd, self.__class__.__name__)
            self.bot.add_command(cmd)

        for _event in self.list_events():
            _event["_module_instance"] = self
            self.bot.add_event_listener(_event["name"], self._event_handler_callback(_event["function"]))

    def __teardown__(self):
        """Teardown function called once by NioBot.unmount_module(). Removes any command that was mounted."""
        for cmd in self.list_commands():
            self.bot.remove_command(cmd)
        del self
