# Getting started / quick start

!!! tip "Want to skip to see some examples?"
    You can see some examples on [GitHub](https://github.com/nexy7574/nio-bot/tree/master/examples)

So, you've joined matrix, had a look around, and now you want to make your own little bot?
Guess what, you can do just that with nio-bot!

## Prerequisites
You will need the following in general:

* A matrix account you can log into (username and password initially)

And the following installed on the machine you want to run the bot on:

* Python with sqlite support
* `libolm` (use your system package manager, like apt or pacman) in order to use end-to-end encryption.
* `libmagic` (usually you can just install `python3-magic`) which is required for attachments.
* A decent network connection (at *least* a few megabits a second, preferably more)
* At least 100mb free storage space (for the database and other files)

## Installation
After you've installed and acquired the above, you can install nio-bot with the following command:
```bash
python3 -m pip install nio-bot[cli]
# Note that we install the extras for `cli` here - the niobot CLI comes with a bunch of useful tools we'll use.
```
If you would like to install support for end-to-end encryption, you can install the following instead:
```bash
python3 -m pip install nio-bot[cli,e2ee]
```


## Creating the start of your bot
In our instance here, we'll create a few files:

1. A `config.py` file to store our configuration.
2. A `main.py` file to store our bot code.
3. A `fun.py` file to store a module (later on).

And you'll need a directory:

4. `store` - this is where nio-bot will store its database and other files.

### File structure
And as such, our directory structure will look like this:
```
test-niobot/
├── config.py
├── fun.py
├── requirements.txt
├── store/
└── main.py
```
!!! danger
    Make sure, if you are using version control, to add `config.py` to your `.gitignore` file! This file contains
    all of your personal information, such as your password, and should not be shared with anyone.

    While you're at it, you should add the `store` directory to your `.gitignore` file as well, as that will contain
    encryption keys later on.

### Setting up config.py

For this example, we will assume you are using <https://matrix.org> as your homeserver.

In our `config.py` file, we'll add the following:

```python
HOMESERVER = "https://matrix-client.matrix.org"
USER_ID = "@my-username:matrix.org"
PASSWORD = "my-password"
```
!!! warning
    Make sure to replace the above with your own homeserver, user ID, and password!

### Making the bot runtime file

And, to make a simple bot, you can just copy the below template into your `main.py` file:

```python
import niobot
import config

bot = niobot.NioBot(
    homeserver=config.HOMESERVER,
    user_id=config.USER_ID,
    device_id='my-device-id',
    store_path='./store',
    command_prefix="!",
    owner_id="@my-matrix-username:matrix.org"
)
# We also want to load `fun.py`'s commands before starting:
bot.mount_module("fun")  # looks at ./fun.py

@bot.on_event("ready")
async def on_ready(_):
    # That first argument is needed as the first result of the sync loop is passed to ready. Without it, this event
    # will fail to fire, and will cause a potentially catasrophic failure.
    print("Bot is ready!")


@bot.command()
async def ping(ctx):  # can be invoked with "!ping"
    await ctx.respond("Pong!")

bot.run(password=config.PASSWORD)
```

???+ warning "About `owner_id`"
    `owner_id` is intended to tell nio-bot who owns the current instance.
    __Do not set this to be the same thing as `config.USER_ID` (your bot's ID)!__
    The only time you should do that is if you want to run the bot on the same account you use.

    Otherwise, set this to be your own user ID, so that you can use any "owner only" commands.

    It is not necessary to set this though, so it can be omitted or set to `None`. Just note that
    `NioBot.is_owner(...)` will raise an error when used in that case.

#### Enabling logging

You'll probably find that it's useful to enable debug logging while you're developing your bot. To do that, you can
add the following to your `main.py` file:
```python
import logging
import niobot

logging.basicConfig(level=logging.DEBUG)
# or to save to a file (uncomment):
# logging.basicConfig(level=logging.DEBUG, filename="bot.log")

bot = niobot.NioBot(...)
...
```

This will print an awful lot of text to your console, but will ultimately be helpful for debugging any
issues you are encountering, as it will show you a lot of what niobot is doing.

### Making fun.py

Now, fun.py is going to be a module.

Modules are a great way to organize your code, and make it easier to manage. They also allow you to
easily add new commands to your bot without having to edit the main file, which means you can split your code up, and
make it... modular!

To start, we need to make the fun.py python file, and add the following:

```python
import niobot


class MyFunModule(niobot.Module):  # subclassing niobot.Module is mandatory for auto-detection.
    def __init__(self, bot):
        super().__init__(bot)
        # This gives you access to `self.bot`, which is the NioBot instance you made in main.py!

```
And that's it! You made your module!

#### But wait, there's more!

You may notice that with this being a separate module, you can't use `@bot.command`, or `@bot.on_event`, or reference
`bot` at all!

You'd initially assume "Oh, I'll just import bot from main." - but that's not going to work. The reason for this is
every time `main.py` is imported, it creates a new [`NioBot`][niobot.client.NioBot], and then... calls bot.run() at the end, meaning not only
would your import never finish, but it would also cause a massive recursion bug!

The way you get around this is instead with `@niobot.command()`. This is a decorator that will register the command
with the bot, however is designed specifically with modules in mind.

Let's compare the two, for simplicity:

| `@niobot.NioBot.command()`                                            | `@niobot.command()`                                                        |
|-----------------------------------------------------------------------|----------------------------------------------------------------------------|
| Adds commands to the register immediately                             | Adds commands to the register once the module is loaded                    |
| Can only be used at runtime, or wherever `bot` can be imported from   | Can only be used in modules (__has no effect outside a` niobot.Module`!__) |
| Takes priority over `@niobot.command()` due to the immediate register | Lower priority than `NioBot.command()` due to the "lazy loading"           |

Do be aware though, both decorators will take the exact same arguments as [`niobot.Command`][niobot.commands.Command].

#### Adding a command to fun.py

So, let's add a command to our module:

```python
import niobot


class MyFunModule(niobot.Module):  # subclassing niobot.Module is mandatory for auto-detection.
    def __init__(self, bot):
        super().__init__(bot)

    @niobot.command()
    async def hello(self, ctx: niobot.Context):
        await ctx.respond("Hello %s!" % ctx.event.sender)
```

This will add a command, `!hello`, that will reply with "Hello {@author}!"

### Starting the bot

Hold your horses, you're not quite ready yet!

Generally, it's a terrible idea to always use a password in your code. It's a security risk,
and in matrix it can result in creating many sessions, which you don't want, especially if you're using encryption!

#### Getting an access token
An access token is like a server-generated long-lived password. You will probably want one in order to repeatedly use
the same session, and to avoid having to use your password in your code.

You can get your password with `niocli get-access-token`.
For example:
```bash
(venv) [me@host test-niobot]$ niocli get-access-token
User ID (@username:homeserver.tld): @test:matrix.org
Password (will not echo):
Device ID (a memorable display name for this login, such as 'bot-production') [host]:
Resolving homeserver... OK
Getting access token... OK
Access token: syt_<...>
```

What you're going to do now, is copy the full access token string, and open `config.py` again
Now, replace `PASSWORD=...` with `ACCESS_TOKEN="syt_<...>"`. Make sure to keep the quotes!

You will also need to go into `main.py`, down to the last line, and replace `password=config.PASSWORD` with
`access_token=config.ACCESS_TOKEN`.

??? question "What is `sso_token`?"
    SSO token is a `S`ingle `S`ign `O`n token, employed by the likes of Mozilla, and is often used for SAML.
    Chances are, if you don't know what it is, you definitely don't need it.
    And if you do need it, you already know what it is, why you need it, and how to get it.

#### Actually running the bot

This is the really simple part, actually. All you need to do now is run `main.py`!

```bash
(venv) [me@host test-niobot]$ python main.py
<insert log spam here>
Bot is ready!
<insert log spam here>
```

!!! warning "Its taking FOREVER to log in! is something going wrong?"
    Nope. It can often take a while (upwards of five minutes in some cases!) for the bot to log in.
    This is because, when you first start the bot, it has to *sync* your entire state with the server.
    This often results in a LOT of IO, and a lot of network waiting, etc.

    You can speed up this process in the future by:

    * Making sure you have `store_path` and a valid store in your configuration. Stores mean that the bot doesn't have
      to re-sync everything every time it starts up.
    * Using an access token instead of a password. This means that the bot doesn't have to log in, and can just start
      syncing immediately, even from the last time it was stopped, which saves a very very large portion of the time
      taken

#### Interesting log output

You may notice that, if you [enabled logging](#enabling-logging), you get some interesting log output.

Some things you will want to keep an eye out for:

- `INFO:niobot.client:Encryption support enabled automatically.` - This means that you have set up requirements for the
  bot to use encryption, and it has detected that it can use encryption, and automatically enabled it, which is good!
- `DEBUG:niobot.client:<module '...' from '...'> does not have its own setup() - auto-discovering commands and events` - This
  means that the bot has detected a module, and is automatically loading it. This is good for most cases.
  You should only worry about this message if you defined your own setup function.
- `DEBUG:niobot.client:Registered command <Command name='...' aliases=[...] disabled=...> into <command_name>` - This simply
  means a command has been added to the internal register.
- `DEBUG:niobot.client:Added event listener <function <function_name> at <address>> for '<event_name>'` - Like the above,
  this simply means an event has been added to the internal register.

### And that's it!
You've successfully made a bot, and got it running!

#### Wait, how do I use it?

nio-bot has a handy dandy auto-join feature - if you just invite your bot's user to a room, assuming all is correct,
within a couple seconds, your bot will automatically join your room!

Then, you can run `!help` to get a list of commands, and `!help <command>` to get help on a specific command.

### Final product

??? abstract "config.py"

    ```python
    HOMESERVER = "https://matrix.org"  # or your homeserver
    USER_ID = "@my-bot:matrix.org"  # your bot account's user ID
    ACCESS_TOKEN = "syt_<...>"  # your bot account's access token
    ```

??? abstract "main.py"

    ```python
    import niobot
    import logging
    import config

    logging.basicConfig(level=logging.INFO, filename="bot.log")

    bot = niobot.NioBot(
        homeserver=config.HOMESERVER,
        user_id=config.USER_ID,
        device_id='my-device-id',
        store_path='./store',
        command_prefix="!",
        owner_id="@my-matrix-username:matrix.org"
    )
    # We also want to load `fun.py`'s commands before starting:
    bot.mount_module("fun")

    @bot.on_event("ready")
    async def on_ready(_):
        # That first argument is needed as the first result of the sync loop is passed to ready. Without it, this event
        # will fail to fire, and will cause a potentially catasrophic failure.
        print("Bot is ready!")


    @bot.command()
    async def ping(ctx):  # can be invoked with "!ping"
        await ctx.respond("Pong!")

    bot.run(access_token=config.ACCESS_TOKEN)
    ```

??? abstract "fun.py"
    ```python
    import niobot


    class MyFunModule(niobot.Module):  # subclassing niobot.Module is mandatory for auto-detection.
        def __init__(self, bot):
            self.bot = bot  # bot is the NioBot instance you made in main.py!

        @niobot.command()
        async def hello(self, ctx):
            await ctx.respond("Hello %s!" % ctx.event.sender)
    ```

## Why is logging in with a password so bad?

Logging in with a password carries more risk than logging in with a token, and is more prone to error.
When you log in with a password with nio-bot, you need to *store* that password.
If your password is leaked, an attacker can create as many sessions as they want, reset your password, etc.
However, with an access token, they're limited to that session, and cannot reset your password.

Furthermore, if you log in with a password, some servers may generate you a completely new session, which
is very slow, and can easily break any e2ee you have.
Unless you are very careful with your environment, you may find yourself with slow startup times,
session spam, and decryption errors.

What you **should** do instead is get an access token.

If you already know how to get yours, that's great! Otherwise, `niocli` has the solution:

```bash
$ niocli get-access-token
```

This will log into the account when prompted, and will grab you an access token, spitting it out into your terminal.

From there, you can replace `bot.run(password="...")` with `bot.run(access_token="...")`, and you're good to go!
