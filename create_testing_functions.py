import classes_functions_game_handlers
import classes_functions_game_objects

def string_to_code():
    #launch in python3 -i
    lines = "a"

    output = ""
    output += ("turn.set_preset([\n")
    lines = input()
    while lines != "" and lines != "EOF":
        output += "["
        lines = lines.split(" ")
        for i in lines:
            output += '"{}", '.format(i)

        output += "],\n"
        lines = input()

    output += (")]")

    print(output)

