# Table of Contents
- [Table of Contents](#table-of-contents)
- [Introduction](#introduction)
- [Principle](#principle)
- [How to use it](#how-to-use-it)
  - [Syntax of `script.txt`](#syntax-of-scripttxt)
    - [Namespace](#namespace)
    - [Dialogue](#dialogue)
    - [Function](#function)
    - [Option](#option)
    - [Title](#title)
    - [Other](#other)

# Introduction

Are you a Minecraft map creator who struggles with converting scripts into datapack commands? Are you tired of manually inputting each dialogue into the tellraw generator and copying the command to the datapack every time? If so, here's the solution! STDG.py (short for Script to Datapack Generator version 2) is a simple Python script that converts dialogue scripts into Minecraft datapacks.

# Principle

The script converts dialogues (or multiple commands) into a chain of function blocks. Each function executes the next function in a queue-like manner. The execution direction follows the pattern `<namespace>:1 -> <namespace>:2 -> <namespace>:3 -> ...`

# How to use it

Simply type `python STDG.py <input_script_path> <output_datapack_path>` to generate the datapack at the `<output_datapack_path>`.

## Syntax of `script.txt`

Inspired by LaTeX, the script.txt file uses the syntax \<command>[kwarg]{<arg>}. The following commands are available for use in this script. For a complete example, refer to the ExampleScript.txt and ExampleDataPack files.

### Namespace

- `\namespace{<namespace>}`: Set the namespace of the following function.

### Dialogue

- `\dialogue[kwarg]{<passage>}`: Set the keyword argument
  - All keyword arguments:
    - `t=<n>`: Set the duration of the dialogue to be `n` seconds. Note that `n` should be integer.
    - Other tellraw argument such as `"color":"dark_aqua", italic=true`: Set the tellraw argument to the dialogue
  - `<passage>`: The script turns the passage to the chain of functions, separated by line break. The duration of the dialogue will be set automatically based on the length of the sentence, if we do not set it manually in keyword argument.

- Example: 
```
\namespace{passage1}

\dialogue{
Even_Gor: hello. My Name is Spaghetti Even. 
Ben: ??
Ryan: hello
}

==>

# In function passage1:1
tellraw @a {"text": "Even_Gor: hello. My Name is Spaghetti Even. "}
schedule function s1p1:4 15s
schedule function passage1:2 15s

# In function passage1:2
tellraw @a {"text": "Ben: ??"}
schedule function s1p1:5 3s

# In function passage1:3
tellraw @a {"text": "Ryan: hello"}
schedule function passage1:4 4s
```


### Function

- `\function[kwarg]{<functions>}`: Add a new function for executing `functions`
  - Keyword argument: `t=<n>`: Set the waiting time to execute the next function to be `n` seconds.

- `\function!{<functions>}`: Add the functions to the current function block.

- `\reset{<functions>}`: Behaves similar to `\function`. It will also adds the function to the reset command. Note that the script generates a function located at `<dp>/functions/reset` to reset the entire datapack.

### Option

- `\option[kwarg]{<dict>}`: Generate an "option" dialogue for player to click it. 
  - `<dict>`: a dictionary with namespace-dialogue pairs. Once the player clicks the dialogue, it will execute the head of that namespace.
  - Keyword argument: 
    - `save=<objective_name>`: Sometimes you need to record what option have the player chosen. Here we save the save the result to `<objective_name>`. The player with `<objective_name>==n` means that he has chosen the `n`th option.
    - `reselect=<bool>`: Allow player to reselect the option. It requires us to set the `save` to use this feature probably.
    - `color=<string>`: Set the color of the option that has not been selected before.
    - `selected_color=<string>`: Set the color of the option that has been selected.
    - `to=<namespace>`: run the `<namespace>:1`, once all options has been selected by player

- Example: See the `ExampleScript.txt` and also the `ExampleDataPack`

### Title 

- `\title[kwarg]{text}`: Generate the title function
  - Keyword argument: 
    - `t=<n>`: Wait for `n` seconds and run the next function.
    - `fade_in=n`: Set the fade in duration as `n` seconds.
    - `fade_out=n`: Set the fade out duration as `n` seconds.
    - `dur=n`: Set the duration of the title as `n` seconds.
    - `color=<string>`: Set the fade in duration as `n` seconds.

### Other

- `\color_map{<dict>}`: Sometimes, we want to use different colors for different characters (before the delimiter). Setting the color map allows us to achieve this. Note that it should be used at the beginning of the script and can be overridden by the keyword argument in the dialogue command.

- Example: 
```
\color_map{
Even_Gor: cyan, 
Ben: red
}

\namespace{s1p1}

\dialogue{
Even_Gor: hello. My Name is Spaghetti Even. 
}

==> 
# In function passage1:1
tellraw @a [{"text": "Even_Gor", "color": "cyan"}, {"text": ": hello. My Name is Spaghetti Even. ", "color": "white"}]
schedule function passage1:2 15s
```

- `\macro[<macro_name>]{<arg>}`: Setting the macro for the script. `$opt` is the placeholder for the keyword argument and `$arg` is the placeholder of the argument.

- Example:

```
\macro[mission]{
dialogue[color=green, $opt]{$arg}; 
function!{execute as @a at @s run playsound minecraft:entity.player.levelup player @s ~ ~ ~}
}

\mission{[Find a way to reach meteor crater]}

==> 
dialogue[color=green]{[Find a way to reach meteor crater]}; 
function!{execute as @a at @s run playsound minecraft:entity.player.levelup player @s ~ ~ ~}

==> 
# In the function
tellraw @a {"color": "green", "text": "[Find a way to reach meteor crater]"}
schedule function s2p3:2 12s
execute as @a at @s run playsound minecraft:entity.player.levelup player @s ~ ~ ~
```

