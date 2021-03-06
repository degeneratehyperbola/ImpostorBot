# Impostor Discord Bot

A programmable Discord bot controlled using an POSIX-like syntax. It has generic functionality of every Discord bot ever but is controlled from the host and not through chat commands. This human interface is pretty bad for some stuff like text messaging or talking in a voice chat, although still alows to do so.

# The Idea
The primal idea for it was to have yet another way of making Your own discord bot that is so easy to program, so high-level, that it loses all its purpose. Hence it is controlled by Impostor Script Notation that was made in, like, 3 minutes with simple POSIX argument parsing.

And yes, it delivers on the promise of doing a little trolling.

# Usage
This repository contains `example.py` file which might seem to be the example but, in fact, holds most of the bot's functionality and the entry point. If You want to just no-brain run it, run aforesaid `example.py` file

**Note: A bot token must be placed inside `config.json` file in the same directory in order for it to work**
```json
{
  "BotToken": "YOUR TOKEN HERE"
}
```

The `example.py` file contains the bot's initialization code (e.g. connecting the bot), most of the instructions definitions, the command prompt itself and consequent keyboard interupts handling and such. You can add custom commands in `example.py` since all of them are registered there.

## What is a command and how to add one
A command/instruction is a Python function that executes when the command is invoked and an alias associated with it and using which the command is indexed. The function can be either generic or asynchronous.

```py
list_of_cmds = {'help': help_fn, 'join': join_channel_fn}
```

A command takes the same parameters that its associated function takes, even the variable ones. All the arguments are converted automatically to the types that are hinted in the Python function. If there is no hint associated, the argument is not converted from its original type - string.

**Note: Keyword only arguments and keyword variable arguments are ignored**

You can add new instructions and make other aliases for existing ones from outside of the ISN context like so:
```py
isn_context.register('alias', function)
```

## Syntax and interpreter features
A simple POSIX-like syntax with no super advanced stuff like detours or nesting.

```ps1
<command> [argument1] [argument2] [argument3]...
```

Grouping is done with quotes (`"` and `'`):
```ps1
<command> "argument ... still the same argument" 'now goes the next one'

# Parsed as: ['argument ... still the same argument', 'now goes the next one']
```

And escaping with a backslash `\` like so:
```ps1
<command> "can have \"funny\" symbols in here, including the \\"

# Parsed as: ['can have "funny" symbols in here, including the \']
```

Set an existing variable or declare a new one:
```ps1
set <variable_name> <value>
```

Set/initialize a variable to a command's return value:
```ps1
setc <variable_name> <command> [arguments]...
```  

Pass a value from a variable as an argument:
```ps1
<command> [arguments] @<variable_name> [arguments]...
```

Comments are done with a hash `#` character:
```ps1
# This is a comment and will be ignored
```

## Usage examples
Read the chat for signs of life (last 10 messages):
```ps1
setch 746316046616625192
chatlog 10
```

Send a chat message:
```ps1
setch 746316046616625192
msg "Hello? Is this chat dead?"
msg "Gonna play some music on #townhall"
```

Play audio from web and from the filesystem:
```ps1
setch 811264974184775691
join
playweb https://www.youtube.com/watch?v=MH1imROLPho&list=PLYZCCGiDf0qijxmpClFxZlVWWyzuwjy2y&index=1
stop
play "D:\Music\*.mp3"
skip
skip
```

## Instruction Set
You can see the list of all implemented commands using the `help` command, however they are not yet documented :P

# Dependancies
- Python 3.10
- discord.py
- PyNaCl (only used for audio)

# TODO List
Each module's TODO list is in their respective files.
