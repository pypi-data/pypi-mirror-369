import importlib
import inspect
from os import path


def botFinder() -> str:
    """Looks in call stack for first robot.py and returns the fully qualified path to that file

    Returns:
        str: Fully qualified path to robot.py from call stack (minus robot.py)
    """
    stack = inspect.stack()
    for f_idx, f_info in enumerate(stack):
        # print(f"robot_info stack {f_idx} {f_info}")
        frame, filename, line_number, function_name, lines, index = stack[f_idx]
        # print(
        #     f"looking for {f_idx} {f_info} {frame}, {filename}, {line_number}, {function_name}, {lines}, {index}"
        # )
        if "robot.py" in filename:
            print(f"FOUND!!! {filename}")
            return path.dirname(filename)
    return None
