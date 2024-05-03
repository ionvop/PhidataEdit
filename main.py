import fractions
import json
import time
import traceback


def main() -> None:
    while True:
        try:
            compile()
        except Exception:
            print()
            print(traceback.format_exc())

        last_content = open("phidata.txt").read()

        while True:
            if open("phidata.txt").read() != last_content:
                break

            time.sleep(1)


def compile() -> None:
    result = {
        "BPMList": [],
        "META" : {
            "RPEVersion" : 140,
            "background" : "",
            "charter" : "",
            "composer" : "",
            "id" : "",
            "level" : "",
            "name" : "",
            "offset" : 0,
            "song" : ""
        },
        "judgeLineGroup" : [ "Default" ],
        "judgeLineList" : [],
        "multiLineString" : "",
        "multiScale" : 1.0
    }

    data = open("phidata.txt").read()
    meta = data[:data.find("&inote=") + 1].strip()
    fumen = data[data.find("&inote=") + 7:].strip()
    key = "id"
    result["META"]["id"] = meta[meta.find(f"&{key}=") + len(f"&{key}="):meta.find("&", meta.find(f"&{key}=") + 1)].strip()
    result["META"]["background"] = result["META"]["id"] + ".png"
    result["META"]["song"] = result["META"]["id"] + ".mp3"
    key = "title"
    result["META"]["name"] = meta[meta.find(f"&{key}=") + len(f"&{key}="):meta.find("&", meta.find(f"&{key}=") + 1)].strip()
    key = "artist"
    result["META"]["composer"] = meta[meta.find(f"&{key}=") + len(f"&{key}="):meta.find("&", meta.find(f"&{key}=") + 1)].strip()
    key = "first"
    result["META"]["offset"] = int(meta[meta.find(f"&{key}=") + len(f"&{key}="):meta.find("&", meta.find(f"&{key}=") + 1)].strip())
    key = "des"
    result["META"]["charter"] = meta[meta.find(f"&{key}=") + len(f"&{key}="):meta.find("&", meta.find(f"&{key}=") + 1)].strip()
    key = "lv"
    result["META"]["level"] = meta[meta.find(f"&{key}=") + len(f"&{key}="):meta.find("&", meta.find(f"&{key}=") + 1)].strip()
    divisor = 1
    beat = (0, 1)
    i = 0
    note_temp = ""
    note_temp_list = []
    note_list = []
    event_list = []

    while i < len(fumen):
        match fumen[i]:
            case "(":
                temp = ""
                i += 1

                while i < len(fumen):
                    if fumen[i] == ")":
                        break

                    temp += fumen[i]
                    i += 1

                result["BPMList"].append({
                    "bpm": float(temp),
                    "startTime": list(simplify_mixed_number((0, beat[0], beat[1])))
                })
            case "{":
                temp = ""
                i += 1

                while i < len(fumen):
                    if fumen[i] == "}":
                        break

                    temp += fumen[i]
                    i += 1

                divisor = int(temp)
            case "$":
                if fumen[i + 1] == "{":
                    temp = ""
                    i += 2

                    while i < len(fumen):
                        if fumen[i] == "\\":
                            temp += fumen[i + 1]
                            i += 2
                            continue

                        if fumen[i: i + 2] == "};":
                            i += 1
                            break

                        temp += fumen[i]
                        i += 1

                    fumen = fumen[:i + 1] + str(eval(temp)) + fumen[i + 1:]
                elif fumen[i + 1:i + 3] == "${":
                    temp = ""
                    i += 3

                    while i < len(fumen):
                        if fumen[i] == "\\":
                            temp += fumen[i + 1]
                            i += 2
                            continue

                        if fumen[i: i + 2] == "};":
                            i += 1
                            break

                        temp += fumen[i]
                        i += 1

                    temp = unindent_multiline_string(temp)
                    exec(temp)
            case "%":
                if fumen[i + 1] == "{":
                    temp = ""
                    i += 2

                    while i < len(fumen):
                        if fumen[i] == "\\":
                            temp += fumen[i + 1]
                            i += 2
                            continue

                        if fumen[i: i + 2] == "};":
                            i += 1
                            break

                        temp += fumen[i]
                        i += 1

                    temp = unindent_multiline_string(temp)
                    temp = indent_multiline_string(temp, 4)
                    temp = f"def _result():\n{temp}"
                    exec(temp)
                    fumen = fumen[:i + 1] + str(eval("_result()")) + fumen[i + 1:]
            case "<":
                if fumen[i + 1] == "=":
                    temp = ""
                    i += 2

                    while i < len(fumen):
                        if fumen[i] == ">":
                            break

                        temp += fumen[i]
                        i += 1

                    temp = [int(x) for x in temp.split(":")]

                    if len(temp) == 3:
                        temp = mixed_to_improper((temp[0], temp[1], temp[2]))

                    beat = temp[0], temp[1]
            case "/":
                note_temp_list.append(note_temp)
                note_temp = ""
            case ",":
                if note_temp.strip() != "":
                    note_temp_list.append(note_temp)

                for element in note_temp_list:
                    element = element.strip()

                    if element[0] in "xyras":
                        end_time = calculate_fractions(beat, "+", (1, 128))

                        event_data = {
                            "type": "moveXEvents",
                            "line": 0,
                            "easingType" : 1,
                            "end" : 0.0,
                            "endTime" : list(simplify_mixed_number((0, end_time[0], end_time[1]))),
                            "start" : 0.0,
                            "startTime" : list(simplify_mixed_number((0, beat[0], beat[1])))
                        }

                        match element[0]:
                            case "x":
                                event_data["type"] = "moveXEvents"
                            case "y":
                                event_data["type"] = "moveYEvents"
                            case "r":
                                event_data["type"] = "rotateEvents"
                            case "a":
                                event_data["type"] = "alphaEvents"
                            case "s":
                                event_data["type"] = "speedEvents"

                        j = 1

                        if element[1] == "[":
                            temp = ""
                            j = 2

                            while j < len(element):
                                if element[j] == "]":
                                    break

                                temp += element[j]
                                j += 1

                            if temp[0] == "#":
                                temp = temp[1:]
                                temp = temp.split(":")
                                event_data["endTime"] = [int(x) for x in temp[:3]]
                            else:
                                temp = temp.split(":")
                                end_time = calculate_fractions(beat, "+", (int(temp[1]) * 4, int(temp[0])))
                                event_data["endTime"] = list(simplify_mixed_number((0, end_time[0], end_time[1])))
                                
                            j += 1

                        parameter = 0
                        temp = ""

                        while j < len(element):
                            if element[j] == ":" or j == len(element) - 1:
                                if j == len(element) - 1:
                                    temp += element[j]

                                match parameter:
                                    case 0:
                                        event_data["line"] = int(temp)
                                    case 1:
                                        event_data["start"] = float(temp)
                                        event_data["end"] = float(temp)
                                    case 2:
                                        event_data["end"] = float(temp)
                                    case 3:
                                        event_data["easingType"] = float(temp)

                                parameter += 1
                                temp = ""
                            else:
                                temp += element[j]

                            j += 1

                        event_list.append(event_data)
                        continue

                    note_data = {
                        "line": 0,
                        "above" : 1,
                        "endTime" : list(simplify_mixed_number((0, beat[0], beat[1]))),
                        "isFake" : 0,
                        "positionX" : 0,
                        "startTime" : list(simplify_mixed_number((0, beat[0], beat[1]))),
                        "type" : 0
                    }

                    match element[0]:
                        case "n":
                            note_data["type"] = 1
                        case "d":
                            note_data["type"] = 4
                        case "f":
                            note_data["type"] = 3

                    j = 1

                    if element[1] == "[":
                        temp = ""
                        j = 2

                        while j < len(element):
                            if element[j] == "]":
                                break

                            temp += element[j]
                            j += 1

                        note_data["type"] = 2

                        if temp[0] == "#":
                            temp = temp[1:]
                            temp = temp.split(":")
                            note_data["endTime"] = [int(x) for x in temp[:3]]
                        else:
                            temp = temp.split(":")
                            end_time = calculate_fractions(beat, "+", (int(temp[1]) * 4, int(temp[0])))
                            note_data["endTime"] = list(simplify_mixed_number((0, end_time[0], end_time[1])))
                            
                        j += 1

                    parameter = 0
                    temp = ""

                    while j < len(element):
                        if element[j] == ":" or j == len(element) - 1:
                            if j == len(element) - 1:
                                temp += element[j]

                            match parameter:
                                case 0:
                                    note_data["line"] = int(temp)
                                case 1:
                                    note_data["positionX"] = float(temp)
                                case 2:
                                    if int(temp) == 1:
                                        note_data["above"] = 2
                                case 3:
                                    if int(temp) == 1:
                                        note_data["isFake"] = 1

                            parameter += 1
                            temp = ""
                        else:
                            temp += element[j]

                        j += 1

                    note_list.append(note_data)

                note_temp = ""
                note_temp_list = []
                beat = calculate_fractions(beat, "+", (4, divisor))
            case "|":
                if fumen[i + 1] == "|":
                    while i < len(fumen):
                        if fumen[i] == "\n":
                            break

                        i += 1
            case "\n":
                pass
            case " ":
                    pass
            case _:
                note_temp += fumen[i]

        i += 1

    line_count = 0

    for element in note_list:
        if element["line"] > line_count:
            line_count = element["line"]

    for element in event_list:
        if element["line"] > line_count:
            line_count = element["line"]

    line_count += 1

    for i in range(line_count):
        result["judgeLineList"].append({
            "Group" : 0,
            "Name" : "Untitled",
            "Texture" : "line.png",
            "alphaControl" : [
                {
                    "alpha" : 1.0,
                    "easing" : 1,
                    "x" : 0.0
                },
                {
                    "alpha" : 1.0,
                    "easing" : 1,
                    "x" : 9999999.0
                }
            ],
            "bpmfactor" : 1.0,
            "eventLayers" : [
                {
                    "alphaEvents" : [],
                    "moveXEvents" : [],
                    "moveYEvents" : [],
                    "rotateEvents" : [],
                    "speedEvents" : []
                }
            ],
            "extended" : {
                "inclineEvents" : [
                    {
                        "bezier" : 0,
                        "bezierPoints" : [ 0.0, 0.0, 0.0, 0.0 ],
                        "easingLeft" : 0.0,
                        "easingRight" : 1.0,
                        "easingType" : 2,
                        "end" : 0.0,
                        "endTime" : [ 1, 0, 1 ],
                        "linkgroup" : 0,
                        "start" : 0.0,
                        "startTime" : [ 0, 0, 1 ]
                    }
                ]
            },
            "father" : -1,
            "isCover" : 1,
            "numOfNotes" : 0,
            "notes": [],
            "posControl" : [
                {
                    "easing" : 1,
                    "pos" : 1.0,
                    "x" : 0.0
                },
                {
                    "easing" : 1,
                    "pos" : 1.0,
                    "x" : 9999999.0
                }
            ],
            "sizeControl" : [
                {
                    "easing" : 1,
                    "size" : 1.0,
                    "x" : 0.0
                },
                {
                    "easing" : 1,
                    "size" : 1.0,
                    "x" : 9999999.0
                }
            ],
            "skewControl" : [
                {
                    "easing" : 1,
                    "skew" : 0.0,
                    "x" : 0.0
                },
                {
                    "easing" : 1,
                    "skew" : 0.0,
                    "x" : 9999999.0
                }
            ],
            "yControl" : [
                {
                    "easing" : 1,
                    "x" : 0.0,
                    "y" : 1.0
                },
                {
                    "easing" : 1,
                    "x" : 9999999.0,
                    "y" : 1.0
                }
            ],
            "zOrder" : 0
        })

    for element in note_list:
        result["judgeLineList"][element["line"]]["notes"].append({
            "above" : element["above"],
            "alpha" : 255,
            "endTime" : element["endTime"],
            "isFake" : element["isFake"],
            "positionX" : element["positionX"],
            "size" : 1.0,
            "speed" : 1.0,
            "startTime" : element["startTime"],
            "type" : element["type"],
            "visibleTime" : 999999.0,
            "yOffset" : 0.0
        })

        if element["type"] != 2:
            result["judgeLineList"][element["line"]]["numOfNotes"] += 1

    for element in event_list:
        result["judgeLineList"][element["line"]]["eventLayers"][0][element["type"]].append({
            "bezier" : 0,
            "bezierPoints" : [ 0.0, 0.0, 0.0, 0.0 ],
            "easingLeft" : 0.0,
            "easingRight" : 1.0,
            "easingType" : element["easingType"],
            "end" : element["end"],
            "endTime" : element["endTime"],
            "linkgroup" : 0,
            "start" : element["start"],
            "startTime" : element["startTime"]
        })

    print(note_list)
    print(event_list)
    open(f"{result['META']['id']}.json", "w").write(json.dumps(result, indent=4))


def calculate_fractions(num1: tuple[int, int], operator: str, num2: tuple[int, int]) -> tuple[int, int]:
    frac1 = fractions.Fraction(*num1)
    frac2 = fractions.Fraction(*num2)
    result = frac1

    match operator:
        case "+":
            result = frac1 + frac2
        case "-":
            result = frac1 - frac2
        case "*":
            result = frac1 * frac2
        case "/":
            result = frac1 / frac2

    return result.numerator, result.denominator

def mixed_to_improper(mixed_num: tuple[int, int, int]) -> tuple[int, int]:
    whole, numerator, denominator = mixed_num
    new_numerator = whole * denominator + numerator
    return (new_numerator, denominator)


def simplify_mixed_number(mixed_num: tuple[int, int, int]) -> tuple[int, int, int]:
    whole, numerator, denominator = mixed_num
    frac = fractions.Fraction(numerator, denominator)
    new_frac = fractions.Fraction(whole) + frac
    new_whole = new_frac.numerator // new_frac.denominator
    new_numerator = new_frac.numerator % new_frac.denominator
    new_denominator = new_frac.denominator
    
    if new_numerator == 0:
        new_denominator = 1
    
    return (new_whole, new_numerator, new_denominator)


def indent_multiline_string(input_string: str, num_spaces: int) -> str:
    lines = input_string.split('\n')
    space_string = ' ' * num_spaces
    indented_lines = [space_string + line for line in lines]
    indented_string = '\n'.join(indented_lines)
    return indented_string

def unindent_multiline_string(input_string: str) -> str:
    lines = input_string.split('\n')
    min_spaces = min(len(line) - len(line.lstrip()) for line in lines if line.strip())
    unindented_lines = [line[min_spaces:] if len(line) - len(line.lstrip()) >= min_spaces else line for line in lines]
    unindented_string = '\n'.join(unindented_lines)
    return unindented_string


def test() -> None:
    test_cases = [
        (0, 0, 1)
    ]

    for case in test_cases:
        print(f"Input: {case} -> Output: {simplify_mixed_number(case)}")

    exit()


if __name__ == "__main__":
    #test()
    main()