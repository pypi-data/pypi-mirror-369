import sys
import re
import inspect
import datetime
import pprint
import logging
import threading
import os
import socket
import getpass
import json
import xml.etree.ElementTree as ET
import yaml

# Configure a basic logger for file output
file_logger = logging.getLogger("eprint_file_logger")
file_logger.setLevel(logging.INFO)

class AnsiColors:
    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    RESET = "\033[0m"

class AnsiBackgroundColors:
    BLACK = "\033[40m"
    RED = "\033[41m"
    GREEN = "\033[42m"
    YELLOW = "\033[43m"
    BLUE = "\033[44m"
    MAGENTA = "\033[45m"
    CYAN = "\033[46m"
    WHITE = "\033[47m"
    RESET = "\033[0m"

class AnsiStyles:
    BOLD = "\033[1m"
    ITALIC = "\033[3m"
    UNDERLINE = "\033[4m"
    STRIKETHROUGH = "\033[9m"
    REVERSE = "\033[7m"
    RESET = "\033[0m"

def _strip_ansi(s):
    return re.sub(r"\x1b\[[0-9;]*m", "", s)

def eprint(*args, 
           sep=", ", 
           end="\n", 
           file=None, 
           flush=False, 
           color=None, 
           bgcolor=None, 
           style=None,
           align=None,
           width=None,
           padding=0,
           border=None,
           box=False,
           var_name=False,
           expression=None,
           timestamp=False,
           line_info=False,
           func_name=False,
           pretty=False,
           type_info=False,
           log_file=None,
           log_level="INFO",
           log_formatter=None,
           thread_info=False,
           process_id=False,
           hostname=False,
           username=False,
           app_name=None,
           max_depth=None,
           sort_keys=False,
           compact=False,
           json_format=False,
           xml_format=False,
           yaml_format=False):
    """
    An enhanced print function with various features.
    """
    output_parts = []
    original_args_str = sep.join(map(str, args))

    # Add contextual information
    if timestamp:
        now = datetime.datetime.now()
        time_format = "%Y-%m-%d %H:%M:%S"
        output_parts.append(f"[{now.strftime(time_format)}]")
    if line_info:
        frame = inspect.currentframe().f_back
        frame_info = inspect.getframeinfo(frame)
        output_parts.append(f"[{frame_info.filename}:{frame_info.lineno}]")
    if func_name:
        frame = inspect.currentframe().f_back
        function_name = frame.f_code.co_name
        output_parts.append(f"[{function_name}()]")
    if thread_info:
        output_parts.append(f"[Thread:{threading.current_thread().name}-{threading.current_thread().ident}]")
    if process_id:
        output_parts.append(f"[PID:{os.getpid()}]")
    if hostname:
        output_parts.append(f"[Host:{socket.gethostname()}]")
    if username:
        output_parts.append(f"[User:{getpass.getuser()}]")
    if app_name:
        output_parts.append(f"[{app_name}]")

    if var_name:
        frame = inspect.currentframe().f_back
        caller_line = inspect.getframeinfo(frame).code_context[0].strip()
        match = re.search(r"eprint\((.*?)\)", caller_line)
        if match:
            arg_strings = [s.strip() for s in match.group(1).split(",")]
            for i, arg_val in enumerate(args):
                try:
                    var_str = arg_strings[i]
                    if re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_]*", var_str):
                        if var_str in frame.f_locals:
                            output_parts.append(f"{var_str}={frame.f_locals[var_str]}")
                        elif var_str in frame.f_globals:
                            output_parts.append(f"{var_str}={frame.f_globals[var_str]}")
                        else:
                            output_parts.append(str(arg_val))
                    else:
                        output_parts.append(str(arg_val))
                except IndexError:
                    output_parts.append(str(arg_val))
        else:
            output_parts.append(original_args_str)
    elif expression:
        frame = inspect.currentframe().f_back
        try:
            evaluated_value = eval(expression, frame.f_globals, frame.f_locals)
            output_parts.append(f"{expression}={evaluated_value}")
        except Exception as e:
            output_parts.append(f"Error evaluating expression \'{expression}\': {e}")
        output_parts.append(original_args_str)
    else:
        if pretty:
            formatted_args = []
            for arg in args:
                if isinstance(arg, (dict, list, tuple, set)):
                    formatted_args.append(pprint.pformat(arg, indent=2, depth=max_depth, compact=compact, sort_dicts=sort_keys))
                else:
                    formatted_args.append(str(arg))
            output_parts.append(sep.join(formatted_args))
        elif json_format:
            try:
                formatted_json = json.dumps(args[0], indent=2, sort_keys=sort_keys)
                output_parts.append(formatted_json)
            except Exception as e:
                output_parts.append(f"Error formatting JSON: {e}")
        elif xml_format:
            try:
                # Assuming the first arg is an ElementTree element or string
                if isinstance(args[0], str):
                    root = ET.fromstring(args[0])
                else:
                    root = args[0]
                # ET.tostring does not have a pretty_print argument directly
                # For pretty printing XML, external libraries like xml.dom.minidom are needed.
                # For now, just convert to string without explicit pretty printing
                formatted_xml = ET.tostring(root, encoding='unicode')
                output_parts.append(formatted_xml)
            except Exception as e:
                output_parts.append(f"Error formatting XML: {e}")
        elif yaml_format:
            try:
                formatted_yaml = yaml.dump(args[0], indent=2, sort_keys=sort_keys)
                output_parts.append(formatted_yaml)
            except Exception as e:
                output_parts.append(f"Error formatting YAML: {e}")
        else:
            output_parts.append(original_args_str)

    if type_info:
        type_info_parts = []
        for arg in args:
            type_info_parts.append(f"({type(arg).__name__})")
        output_parts.append("Types: " + ", ".join(type_info_parts))

    output = " ".join(output_parts)

    # Apply styles
    if style:
        if style == "bold":
            output = AnsiStyles.BOLD + output + AnsiStyles.RESET
        elif style == "italic":
            output = AnsiStyles.ITALIC + output + AnsiStyles.RESET
        elif style == "underline":
            output = AnsiStyles.UNDERLINE + output + AnsiStyles.RESET
        elif style == "strikethrough":
            output = AnsiStyles.STRIKETHROUGH + output + AnsiStyles.RESET
        elif style == "reverse":
            output = AnsiStyles.REVERSE + output + AnsiStyles.RESET

    # Apply colors
    if color:
        if color == "black":
            output = AnsiColors.BLACK + output + AnsiColors.RESET
        elif color == "red":
            output = AnsiColors.RED + output + AnsiColors.RESET
        elif color == "green":
            output = AnsiColors.GREEN + output + AnsiColors.RESET
        elif color == "yellow":
            output = AnsiColors.YELLOW + output + AnsiColors.RESET
        elif color == "blue":
            output = AnsiColors.BLUE + output + AnsiColors.RESET
        elif color == "magenta":
            output = AnsiColors.MAGENTA + output + AnsiColors.RESET
        elif color == "cyan":
            output = AnsiColors.CYAN + output + AnsiColors.RESET
        elif color == "white":
            output = AnsiColors.WHITE + output + AnsiColors.RESET

    # Apply background colors
    if bgcolor:
        if bgcolor == "black":
            output = AnsiBackgroundColors.BLACK + output + AnsiBackgroundColors.RESET
        elif bgcolor == "red":
            output = AnsiBackgroundColors.RED + output + AnsiBackgroundColors.RESET
        elif bgcolor == "green":
            output = AnsiBackgroundColors.GREEN + output + AnsiBackgroundColors.RESET
        elif bgcolor == "yellow":
            output = AnsiBackgroundColors.YELLOW + output + AnsiBackgroundColors.RESET
        elif bgcolor == "blue":
            output = AnsiBackgroundColors.BLUE + output + AnsiBackgroundColors.RESET
        elif bgcolor == "magenta":
            output = AnsiBackgroundColors.MAGENTA + output + AnsiBackgroundColors.RESET
        elif bgcolor == "cyan":
            output = AnsiBackgroundColors.CYAN + output + AnsiBackgroundColors.RESET
        elif bgcolor == "white":
            output = AnsiBackgroundColors.WHITE + output + AnsiBackgroundColors.RESET

    # Calculate visible length for alignment
    visible_output = _strip_ansi(output)
    current_width = len(visible_output)

    # Apply padding and alignment
    if width and align:
        if width > current_width:
            if align == "left":
                output += " " * (width - current_width)
            elif align == "right":
                output = " " * (width - current_width) + output
            elif align == "center":
                left_pad = (width - current_width) // 2
                right_pad = width - current_width - left_pad
                output = " " * left_pad + output + " " * right_pad

    # Apply borders and boxing
    if box or border:
        box_char_h = "-"  # Horizontal character
        box_char_v = "|"  # Vertical character
        box_char_corner = "+" # Corner character

        if border == "double":
            box_char_h = "=" 
            box_char_v = "|"
            box_char_corner = "+"
        elif border == "single":
            box_char_h = "-" 
            box_char_v = "|"
            box_char_corner = "+"
        elif box: # Default box if box=True and no specific border
            box_char_h = "*"
            box_char_v = "*"
            box_char_corner = "*"

        # Apply padding before calculating border width
        padded_content = visible_output
        if padding > 0:
            padded_content = " " * padding + padded_content + " " * padding

        border_width = len(padded_content) + 2 # +2 for vertical chars

        top_bottom_border = box_char_corner + box_char_h * (border_width - 2) + box_char_corner
        middle_line = box_char_v + padded_content + box_char_v
        
        output = f"{top_bottom_border}\n{middle_line}\n{top_bottom_border}"

    # Print to console or specified file
    print(output, sep=sep, end=end, file=file, flush=flush)

    # Handle logging to file
    if log_file:
        if not file_logger.handlers:
            file_handler = logging.FileHandler(log_file)
            if log_formatter:
                file_handler.setFormatter(logging.Formatter(log_formatter))
            file_logger.addHandler(file_handler)

        log_level_map = {
            "DEBUG": logging.DEBUG,
            "INFO": logging.INFO,
            "WARNING": logging.WARNING,
            "ERROR": logging.ERROR,
            "CRITICAL": logging.CRITICAL,
        }
        file_logger.setLevel(log_level_map.get(log_level.upper(), logging.INFO))
        file_logger.log(log_level_map.get(log_level.upper(), logging.INFO), _strip_ansi(output))


# Example Usage (for testing during development)
if __name__ == "__main__":
    def test_function():
        eprint("Hello from test function!", func_name=True)
        my_dict = {"key1": "value1", "key2": [1, 2, 3]}
        my_list = [1, 2, {"nested": "dict"}]
        eprint(my_dict, pretty=True)
        eprint(my_list, pretty=True)
        eprint("String", 123, [1, 2, 3], type_info=True)

    eprint("Hello, World!")
    eprint("This is a bold message.", style="bold")
    eprint("This is a red message.", color="red")
    eprint("This is a bold and green message.", style="bold", color="green")
    eprint("Underlined text.", style="underline")
    eprint("Cyan text with italic style.", color="cyan", style="italic")
    eprint("Red background.", bgcolor="red")
    eprint("Blue text on yellow background.", color="blue", bgcolor="yellow")
    eprint("Left aligned text", align="left", width=40, color="green")
    eprint("Right aligned text", align="right", width=40, color="blue")
    eprint("Centered text", align="center", width=40, color="magenta")
    eprint("Text with single border", border="single", padding=2)
    eprint("Text with double border", border="double", padding=2)
    eprint("Text in a box", box=True, color="yellow", padding=2)
    eprint("Another text in a box", box=True, border="single", color="cyan", padding=2)

    # Debugging features
    my_variable = 123
    another_var = "test"
    eprint(my_variable, var_name=True)
    eprint(another_var, var_name=True)
    eprint(my_variable + 10, expression="my_variable + 10")
    eprint("Is it true?", expression="my_variable > 100")

    # Contextual information features
    eprint("Message with timestamp", timestamp=True)
    eprint("Message with line info", line_info=True)
    eprint("Message with function name", func_name=True)
    eprint("Message with thread info", thread_info=True)
    eprint("Message with process ID", process_id=True)
    eprint("Message with hostname", hostname=True)
    eprint("Message with username", username=True)
    eprint("Message with app name", app_name="MyAwesomeApp")

    test_function()

    # File logging
    eprint("This message goes to a file.", log_file="eprint.log", log_level="INFO")
    eprint("This is a warning message.", log_file="eprint.log", log_level="WARNING", log_formatter="%(levelname)s: %(message)s")
    eprint("This is a debug message.", log_file="eprint.log", log_level="DEBUG")

    # Data structure pretty-printing
    complex_dict = {
        "name": "John Doe",
        "age": 30,
        "isStudent": False,
        "courses": [
            {"title": "Math", "grade": "A"},
            {"title": "Science", "grade": "B"}
        ],
        "address": {
            "street": "123 Main St",
            "city": "Anytown",
            "zip": "12345"
        }
    }
    eprint("Pretty print complex dict:", complex_dict, pretty=True)
    eprint("Pretty print complex dict (max depth 1):", complex_dict, pretty=True, max_depth=1)
    eprint("Pretty print complex dict (sorted keys):", complex_dict, pretty=True, sort_keys=True)
    eprint("Pretty print complex dict (compact):", complex_dict, pretty=True, compact=True)

    json_data = complex_dict # Use the dict directly for json.dumps
    eprint(json_data, json_format=True)

    xml_string = "<root><item id=\"1\"><name>Test</name></item><item id=\"2\"><name>Another</name></item></root>"
    eprint(xml_string, xml_format=True)

    yaml_data = {"key": "value", "list": [1, 2, 3]}
    eprint(yaml_data, yaml_format=True)


