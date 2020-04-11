import classes_functions_game_handlers
import classes_functions_game_objects

def string_to_code(filename):
    infile = open(filename, "r")
    string = [line.strip() for line in infile.readlines()]
    output = "turn.set_preset([\n"

    for i in string:
        output += "["
        characters = i.split(" ")
        for j in characters:
            output += '"{}",'.format(j)

        output = output[:-1]
        output += "],\n"

    output = output[:-2]
    output += "\n)]"
    print(output)

string_to_code("stringin.txt")
