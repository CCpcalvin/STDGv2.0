# -*- coding: UTF-8 -*-

import re, os, json, sys

from shutil import rmtree
from math import ceil


# Global Variable
DATAPACK_PATH = "."
PACK_FORMAT = 15
DATAPACK_DESCRIPTION = "現代劍俠2天外飛仙 數據包"
WORD_PER_SECOND = 3
DELIMITER = ":"

OPTION_COLOR = "green"
SELECTED_OPTION_COLOR = "gray"
OPTION_SOUND = "minecraft:block.anvil.step"
SELECT_DELAY = "1s"
MAX_OPT = 5

HELPER_OBJ = "Helper"
LOOP_PERIOD = "2t"


# Pattern to detect
STR_PATTERN = [
    "dialogue",  # Done
    "namespace",  # Done
    "function",  # Done
    "function!",  # Done
    "option",  # Done
    "title",  # Done
    "color_map",  # Done
    "macro",  # Done
    "reset",  # Done
]


def readfile(input_file: str) -> list:
    with open(input_file, "r", encoding="utf-8") as f:
        str = f.read()

    # Separate string
    raw_data = find_action(str)

    # Create lists of dictionary
    list_of_actions = []

    # Standardize the data and return error for unknown keyword
    for elem in raw_data:
        # Make a dictionary and store it in lists_of_actions
        action = {"action": elem[0], "arg": elem[2].strip()}

        if elem[1] != "":
            action["opt"] = re.match(r"\[([\w\W]+)\]", elem[1]).group(1).strip()

        list_of_actions.append(action)

    return list_of_actions


# Find all actions in `file_input`
def find_action(str: str) -> list:
    # Separate string by "\\"
    raw_actions = re.findall(r"\\(\w+[!?]*)(\[[\w\W]+?\])?([\w\W]+?)(?=(\\|\Z))", str)

    # Format the last pair of string
    # Extract the string inside the outermost balanced bracket
    actions_list = []
    for raw_action in raw_actions:
        action_list = list(raw_action)
        # Format the last pair of string
        action_list[2] = re.search(r"\{([\w\W]*)\}", action_list[2]).group(1)

        # Add action_list to actions_list
        actions_list.append(action_list)

    return actions_list


def check_namespace(namespace: str):
    if namespace == "":
        exit(
            "Error: Namespace is not available. Use \\namespace before generate any .mcfunction"
        )


def create_datapack(datapack_path: str, datapack_name: str) -> str:
    cursor = os.path.join(datapack_path, datapack_name)

    # Delete the datapack if it exists
    if datapack_name in os.listdir(datapack_path):
        rmtree(cursor)

    # Create new directory
    os.mkdir(cursor)

    os.mkdir(os.path.join(cursor, "data"))

    # Create .mcmeta file
    with open(os.path.join(cursor, "pack.mcmeta"), "w", encoding="utf-8") as f:
        f.write(gen_mcmeta(PACK_FORMAT, DATAPACK_DESCRIPTION))

    return os.path.join(cursor, "data")


def insert_color_map(action: dict) -> dict:
    str_list = action["arg"].split(",")
    color_map = {}

    for string in str_list:
        res = re.search(r"([\w\W]+)" + DELIMITER + r"\s*([\w\W]+)", string)
        if res != None:
            color_map[res.group(1).strip()] = res.group(2).strip()

    return color_map


def insert_macro(action: dict, macro: dict) -> dict:
    macro[action["opt"]] = action["arg"]
    return macro


def gen_mcmeta(pack_format: int, description: str) -> str:
    MCMETA = {"pack": {"pack_format": pack_format, "description": description}}
    return json.dumps(MCMETA, ensure_ascii=False)


def create_namespace(base_cursor: str, namespace: str) -> str:
    # Create namespace directory if it does not exists
    current_cursor = os.path.join(base_cursor, namespace)
    if not os.path.exists(current_cursor):
        os.mkdir(current_cursor)

    # Create functions directory if it does not exists
    current_cursor = os.path.join(current_cursor, "functions")
    if not os.path.exists(current_cursor):
        os.mkdir(current_cursor)

    return current_cursor


def gen_func(cursor: str, action: dict, namespace: str, counter: int) -> int:
    # Check namespace
    check_namespace(namespace)

    # Create new .mcfunction
    with open(
        os.path.join(cursor, f"{counter}.mcfunction"), "w", encoding="utf-8"
    ) as f:
        f.write(action["arg"] + "\n")

        try:
            t = re.search(r"t\s*=\s*([\w\d]+)", action["opt"]).group(1)
        except:
            exit(
                "Error: Wrong optional argument for \\function. Time need to be specified"
            )

        if t != "end":
            f.write(f"schedule function {namespace}:{counter + 1} {t}s\n")

    return counter + 1


def gen_vfunc(cursor: str, action: dict, counter: int):
    # Append
    with open(
        os.path.join(cursor, f"{counter - 1}.mcfunction"), "a", encoding="utf-8"
    ) as f:
        f.write(action["arg"] + "\n")


def get_dur(str: str) -> int:
    res = re.search(r"：([\w\W]+)", str)
    if res != None:
        str = res.group(1)

    t = ceil(len(str) / WORD_PER_SECOND)

    if t < 2:
        return 2
    else:
        return ceil(len(str) / WORD_PER_SECOND)


def get_tellraw(str: str, opt: dict, color_map: dict) -> str:
    # String formatting if not option is given
    if opt == {}:
        json_list = []
        str_list = str.split(DELIMITER)
        if str_list[0] in color_map.keys():
            # Turn char. name to colored name
            json_list.append({"text": str_list[0], "color": color_map[str_list[0]]})
            json_list.append({"text": DELIMITER + str_list[1], "color": "white"})
            return json.dumps(json_list, ensure_ascii=False)

    opt["text"] = str
    return json.dumps(opt, ensure_ascii=False)


def gen_dial(
    cursor: str, action: dict, namespace: str, counter: int, color_map: dict
) -> int:
    # Check namespace
    check_namespace(namespace)

    dialogues = action["arg"].split("\n")
    opt = {}
    all_t = 0

    # Insert optional argument
    if "opt" in action:
        res = re.findall(r"(\w+)\s*=\s*([\w\d]+)", action["opt"])
        for pair in res:
            # If the keyword is t
            if pair[0] == "t":
                all_t = pair[1]
            else:
                # If the argument is true, then make it boolean
                if pair[1] == "true":
                    opt[pair[0]] = bool(pair[1])

                else:
                    opt[pair[0]] = pair[1]

    # Loop over dialogue
    for dialogue in dialogues:
        with open(
            os.path.join(cursor, f"{counter}.mcfunction"), "w", encoding="utf-8"
        ) as f:
            tellraw_json = get_tellraw(dialogue, opt, color_map)
            f.write(f"tellraw @a {tellraw_json}\n")

            # Get time
            if all_t == 0:
                f.write(
                    f"schedule function {namespace}:{counter + 1} {get_dur(dialogue)}s\n"
                )
            else:
                f.write(f"schedule function {namespace}:{counter + 1} {all_t}s\n")

        # Set counter and reset opt
        counter += 1
        opt = {}

    return counter


def gen_title(cursor: str, action: dict, namespace: str, counter: int) -> int:
    # Check namespace
    check_namespace(namespace)

    # Default variable
    t = 5
    title_config = {"dur": 3, "fade_in": 1, "fade_out": 1}
    opt = {}

    # Extract optional argument
    if "opt" in action:
        res = re.findall(r"(\w+)\s*=\s*([\w\d]+)", action["opt"])
        for pair in res:
            # If the keyword is t
            if pair[0] == "t":
                t = pair[1]

            # If the keyword related to title config
            elif pair[0] in title_config:
                title_config[pair[0]] = pair[1]

            else:
                # If the argument is true, then make it boolean
                if pair[1].lower() == "true":
                    opt[pair[0]] = bool(pair[1])

                else:
                    opt[pair[0]] = pair[1]

    # Get text json
    opt["text"] = action["arg"]
    text_json = json.dumps(opt, ensure_ascii=False)

    # Unpack the title_config for writing file
    # Turn second to ticks
    fade_in = int(title_config["fade_in"]) * 20
    dur = int(title_config["dur"]) * 20
    fade_out = int(title_config["fade_out"]) * 20

    # Write file
    with open(
        os.path.join(cursor, f"{counter}.mcfunction"), "w", encoding="utf-8"
    ) as f:
        f.write(f"title @a times {fade_in} {dur} {fade_out}\n")
        f.write(f"title @a title {text_json}\n")
        f.write(f"schedule function {namespace}:{counter + 1} {t}s\n")

    counter += 1
    return counter


def gen_opt_reset(current_cursor: str, counter: int):
    print(f"opt reset at {current_cursor}, {counter}")
    with open(
        os.path.join(current_cursor, f"{counter}.mcfunction"), "a", encoding="utf-8"
    ) as f:
        f.write(f"scoreboard objectives add {HELPER_OBJ} dummy\n")
        for i in range(MAX_OPT):
            f.write(f"scoreboard players set option{i + 1} {HELPER_OBJ} 0\n")


def gen_options(
    current_cursor: str,
    base_cursor: str,
    action: dict,
    namespace: str,
    counter: int,
    obj_create: list,
) -> int:
    # Extract information from text
    # Get text to namespace dict
    options_dict = {}
    str_list = action["arg"].split(",")

    for string in str_list:
        res = re.search(r"([\w\W]+):\s*([\w\W]+)", string)
        if res != None:
            options_dict[res.group(2).strip()] = res.group(1).strip()

    # Extract optional information
    optional_dict = {}

    if "opt" in action:
        opt_str_list = action["opt"].split(",")

        for string in opt_str_list:
            res = re.search(r"([\w\W]+)\s*=\s*([\w\W]+)", string)
            if res != None:
                optional_dict[res.group(1).strip()] = res.group(2).strip()

    # If the optional argument "to" is given, detect whether all option is selected or not first
    if "to" in optional_dict:
        if "save" not in optional_dict:
            exit('Error: "save" is not given in \\option')

        number_of_option = len(options_dict)
        start_counter = counter
        option_counter = counter + number_of_option

        # Or condition chain
        for i in range(number_of_option - 1):
            # Write the header file that detect all option
            with open(
                os.path.join(current_cursor, f"{counter}.mcfunction"),
                "w",
                encoding="utf-8",
            ) as f:
                opt_save_obj = optional_dict["save"]
                f.write(
                    f"execute if score option{i + 1} {opt_save_obj} matches 1 run function {namespace}:{counter + 1}\n"
                )
                f.write(
                    f"execute unless score option{i + 1} {opt_save_obj} matches 1 run function {namespace}:{option_counter}\n"
                )
            counter += 1

        # Add scoreboard at the beginning
        with open(
            os.path.join(current_cursor, f"{start_counter}.mcfunction"),
            "a",
            encoding="utf-8",
        ) as f:
            f.write(f"scoreboard objectives add {opt_save_obj} dummy\n")

        # Write the last mcfunction
        with open(os.path.join(current_cursor, f"{counter}.mcfunction"), "w") as f:
            next_namespace = optional_dict["to"]
            f.write(
                f"execute if score option{number_of_option} {opt_save_obj} matches 1 run function {next_namespace}:1\n"
            )
            f.write(
                f"execute unless score option{number_of_option} {opt_save_obj} matches 1 run function {namespace}:{option_counter}\n"
            )
            counter += 1

    # Create new objective and enable it
    # Also print option start
    trigger_obj = f"{namespace}_trigger"
    # # Hardcode mcfunction for scoreboard
    with open(
        os.path.join(current_cursor, f"{counter}.mcfunction"), "a", encoding="utf-8"
    ) as f:
        f.write(f"scoreboard objectives add {trigger_obj} trigger\n")
        f.write(f"scoreboard objectives add {HELPER_OBJ} dummy\n")
        f.write(f"scoreboard players set detect {HELPER_OBJ} 1\n")
        f.write(f"scoreboard players enable @a {trigger_obj}\n")
        f.write(f"schedule function {namespace}:{counter + 1} 1s\n")

        if "header" not in optional_dict:
            json_text = {"text": "請選擇："}
            if OPTION_COLOR != "":
                json_text["color"] = OPTION_COLOR

            f.write(f"tellraw @a {json.dumps(json_text, ensure_ascii=False)}\n")

        else:
            if optional_dict["header"].lower() == "true":
                json_text = {"text": "請選擇："}
                if OPTION_COLOR != "":
                    json_text["color"] = OPTION_COLOR

                f.write(f"tellraw @a {json.dumps(json_text, ensure_ascii=False)}\n")

        # Add new objective to load if "save" in opt
        # Also initialize the counter variable
        if "save" in optional_dict:
            opt_save_obj = optional_dict["save"]
            if opt_save_obj not in obj_create:
                obj_create.append(opt_save_obj)

    # Hardcode mcfunction for option text
    for i, option in enumerate(options_dict):
        # Hardcode mcfunction for options
        with open(
            os.path.join(current_cursor, f"{counter + i + 1}.mcfunction"),
            "w",
            encoding="utf-8",
        ) as f:
            # Get tellraw json
            json_text = {
                "text": option,
                "clickEvent": {
                    "action": "run_command",
                    "value": f"/trigger {trigger_obj} set {i + 1}",
                },
            }

            # Custom color override default color
            if "color" in optional_dict:
                json_text["color"] = optional_dict["color"]

            # If default color is given in program
            elif OPTION_COLOR != "":
                json_text["color"] = OPTION_COLOR

            # If selected color is not specify, or "save" is not in opt
            if "save" not in optional_dict:
                # Write tellraw
                f.write(f"tellraw @a {json.dumps(json_text, ensure_ascii=False)}\n")

            else:
                # Selected text json
                # Re-clickable if reselect=true
                if "reselect" in optional_dict:
                    if optional_dict["reselect"].lower() == "true":
                        json_selected_text = json_text.copy()
                    else:
                        json_selected_text = {
                            "text": option,
                            "color": SELECTED_OPTION_COLOR,
                        }

                # Not clickable json text
                else:
                    json_selected_text = {
                        "text": option,
                        "color": SELECTED_OPTION_COLOR,
                    }

                # Custom color override default color
                if "selected_color" in optional_dict:
                    json_selected_text["color"] = optional_dict["selected_color"]

                # If default selected color is not specify, or it has the same color as OPTION_COLOR
                elif SELECTED_OPTION_COLOR == "":
                    json_selected_text["color"] = OPTION_COLOR

                else:
                    json_selected_text["color"] = SELECTED_OPTION_COLOR

                # Write score dependent tellraw
                save_obj = optional_dict["save"]
                f.write(
                    f"execute unless score option{i + 1} {save_obj} matches 1 run tellraw @a {json.dumps(json_text, ensure_ascii=False)}\n"
                )
                f.write(
                    f"execute if score option{i + 1} {save_obj} matches 1 run tellraw @a {json.dumps(json_selected_text, ensure_ascii=False)}\n"
                )

            f.write(f"schedule function {namespace}:{counter + i + 2} 1s\n")
            f.write(
                f"execute as @a at @s run playsound {OPTION_SOUND} player @s ~ ~ ~\n"
            )

    # Hardcode mcfunction for score detection
    detect_file_name = counter + len(options_dict) + 1
    with open(
        os.path.join(current_cursor, f"{detect_file_name}.mcfunction"),
        "w",
        encoding="utf-8",
    ) as f:
        for i, option in enumerate(options_dict):
            next_namespace = options_dict[option]
            f.write(
                f"execute as @r[scores={{{trigger_obj}={i + 1}}}] run function {next_namespace}:0 \n"
            )

        f.write(
            f"execute if score detect {HELPER_OBJ} matches 1 run schedule function {namespace}:{detect_file_name} {LOOP_PERIOD}\n"
        )

    # Hardcode mcfunction for stopping detection
    for i, option in enumerate(options_dict):
        next_namespace = options_dict[option]
        current_cursor = create_namespace(base_cursor, next_namespace)
        reset_path = os.path.join(current_cursor, "0.mcfunction")
        if os.path.exists(reset_path):
            with open(
                os.path.join(current_cursor, "0.mcfunction"), "a", encoding="utf-8"
            ) as f:
                f.write(f"scoreboard objectives remove {trigger_obj}\n")
        else:
            with open(
                os.path.join(current_cursor, "0.mcfunction"), "w", encoding="utf-8"
            ) as f:
                f.write(f"scoreboard players set detect {HELPER_OBJ} 0\n")
                f.write(f"scoreboard objectives remove {trigger_obj}\n")
                f.write(f"schedule function {next_namespace}:1 {SELECT_DELAY}\n")

                # Record the option chosen if the optional argument "save" is given
                if "save" in optional_dict:
                    f.write(f"scoreboard players set option{i + 1} {save_obj} 1\n")

    return detect_file_name + 1, obj_create


def gen_file(
    list_of_actions: list,
    base_cursor: str,
    current_cursor: str,
    namespace: str,
    counter: int,
    color_map: dict,
    macro: dict,
    obj_create: list,
    reset_command: list,
) -> tuple:
    # Loop over action
    for idx, action in enumerate(list_of_actions):
        # For action "namespace"
        if action["action"] == "namespace":
            namespace = action["arg"]
            current_cursor = create_namespace(base_cursor, namespace)
            counter = 1

        # Write color map
        elif action["action"] == "color_map":
            color_map = insert_color_map(action)

        # Write macro
        elif action["action"] == "macro":
            macro = insert_macro(action, macro)

        # Create .mcfunction for different files
        elif action["action"] == "function":
            counter = gen_func(current_cursor, action, namespace, counter)

        elif action["action"] == "function!":
            gen_vfunc(current_cursor, action, counter)

        elif action["action"] == "dialogue":
            counter = gen_dial(current_cursor, action, namespace, counter, color_map)

        elif action["action"] == "title":
            counter = gen_title(current_cursor, action, namespace, counter)

        elif action["action"] == "opt_reset":
            gen_opt_reset(current_cursor, counter)

        elif action["action"] == "option":
            counter, obj_create = gen_options(
                current_cursor, base_cursor, action, namespace, counter, obj_create
            )

        elif action["action"] == "reset":
            reset_command.append(action["arg"])

        # Generate file if the action is one of the macro
        elif action["action"] in macro:
            command_str = macro[action["action"]].replace("$arg", action["arg"])
            # If it has optional argument, replace $opt to optional, otherwise replace by ""
            if "opt" in action:
                command_str = command_str.replace("$opt", action["opt"])
            else:
                command_str = command_str.replace("$opt", "")

            # Construct new action list
            new_list_of_action = []
            for command in command_str.split(";"):
                # Add new action
                action = {}
                match = re.search(r"([\w\W]+?)(\[[\w\W]*\])?\{([\w\W]*)\}", command)
                action["action"] = match.group(1).strip()
                action["arg"] = match.group(3).strip()

                # Add optional argument if it has
                if match.group(2) != None:
                    action["opt"] = match.group(2).strip()

                new_list_of_action.append(action)

            # Run the new list of action
            counter, obj_create, reset_command = gen_file(
                new_list_of_action,
                base_cursor,
                current_cursor,
                namespace,
                counter,
                color_map,
                macro,
                obj_create,
                reset_command,
            )

        # Return error for unknown keyword
        elif action["action"] not in STR_PATTERN:
            unknown_action = action["action"]
            exit(f"Error: Unknown keyword for {unknown_action}")

    # Return counter
    return counter, obj_create, reset_command


def gen_helper(
    base_cursor: str, datapack_name: str, obj_create: list, reset_command: list
):
    datapack_name = datapack_name.lower()

    # Create load.json
    current_cursor = os.path.join(base_cursor, "minecraft", "tags", "functions")
    os.makedirs(current_cursor)
    with open(os.path.join(current_cursor, "load.json"), "w", encoding="utf-8") as f:
        f.write(json.dumps({"values": [f"{datapack_name}:load"]}))

    # Create load.mcfunction under minecraft namespace
    current_cursor = os.path.join(base_cursor, datapack_name, "functions")
    os.makedirs(current_cursor)
    with open(
        os.path.join(current_cursor, "load.mcfunction"), "w", encoding="utf-8"
    ) as f:
        for obj in obj_create:
            f.write(f"scoreboard objectives add {obj} dummy\n")

    # Create reset.mcfunction under minecraft namespace
    with open(
        os.path.join(current_cursor, "reset.mcfunction"), "w", encoding="utf-8"
    ) as f:
        for obj in obj_create:
            f.write(f"scoreboard objectives remove {obj}\n")

        # Add reset command to reset.mcfunction
        for elem in reset_command:
            f.write(f"{elem}\n")

        f.write(f"function {datapack_name}:load\n")


# Main function
def main():
    # Check input
    if len(sys.argv) != 3:
        exit("Error: Invalid syntax. Use python STDG.py <input> <output>")

    # Print generating
    print("The datapack is generating...")

    # Set variable
    script_path = sys.argv[1]
    datapack_name = sys.argv[2]

    list_of_actions = readfile(script_path)
    base_cursor = create_datapack(DATAPACK_PATH, datapack_name)
    current_cursor = base_cursor
    namespace = ""
    counter = 1

    color_map = {}
    macro = {}
    obj_create = []
    reset_command = []

    _, obj_create, reset_command = gen_file(
        list_of_actions,
        base_cursor,
        current_cursor,
        namespace,
        counter,
        color_map,
        macro,
        obj_create,
        reset_command,
    )

    # Get helper mcfunction
    gen_helper(base_cursor, datapack_name, obj_create, reset_command)

    # Print feedback
    print("The datapack is generated successfully.")


if __name__ == "__main__":
    main()
