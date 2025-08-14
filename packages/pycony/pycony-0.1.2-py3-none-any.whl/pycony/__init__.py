"""
pyCony is a small utility package for python projects debugging, reverse engineering and tracing

Installation:
    pip install pyCony
        OR
    pip install pip install git+https://github.com/rzbhatti/pyCony.git

Usage:
    from pycony import *

Functions:
    open_console()
    print_stack(depth=None)
    pickle_args(n, pkl_suffix=None, file_path=None)
    print_stack(depth=None)
    load_pickled_args(file_path)
    open_console_print_stack(depth=None)

"""

import code
import inspect
import readline
import pickle
import pdb

# The Python Debugger is very versatile -- https://docs.python.org/3/library/pdb.html -- import pdb; pdb.set_trace()
# Yet at times, we wish if we could interject the code, to view, interact or modify the variables or the objects
# This cute little module takes care of that wish

readline.clear_history()


def open_console():
    """
    Opens an interactive Python console with access to the current scope.
    Includes a try-except block to prevent crashes during console initialization.
    Accesses both local and global variables.
    """
    frame = inspect.currentframe().f_back
    globals_dict = frame.f_globals
    locals_dict = frame.f_locals

    # Combine locals and globals into a single dictionary for the console
    combined_scope = locals_dict.copy()
    combined_scope.update(globals_dict)

    try:
        console = code.InteractiveConsole(combined_scope)
        console.interact(
            banner="Use Ctrl+D (or quit()) to exit and resume program flow."
        )
    except Exception as e:
        print(f"Error initializing interactive console: {e}")


def print_stack(depth=None):
    """
    Crawl the stack to an optional `depth` and print the functions that are called
    along with the arguments passed
    """
    if depth is not None:
        depth += 1
    frame = inspect.currentframe()
    call_stack = inspect.getouterframes(frame, 0)

    print("=" * 25, " Interactive Console: Stack ", "=" * 25)
    for i, frame_info in enumerate(
        reversed(list(call_stack[1:depth]))
    ):  # Skip the current frame
        frame = frame_info.frame
        function_name = frame_info.function
        arguments = inspect.getargvalues(frame).locals

        print(f"  {i + 1}. Function: {function_name}")
        print("     Arguments:")
        for arg_name, arg_value in arguments.items():
            print(f"       {arg_name} = {repr(arg_value)}")
        print("=" * 80)


def pickle_args(n, pkl_suffix=None, file_path=None):
    """
    Pickles the arguments of the function call at stack position n
    (relative to the open_interactive_console call) to the given file path.
    Args:
        n (int): The stack position (1 for the immediate caller, 2 for its caller, etc.).
        file_path (optional str): The full path to the file where the arguments will be pickled.
        pkl_suffix (optional str): ignore if file_path is passed else file_path = '_'.join([target_frame_info.function,pkl_suffix])+'.pkl'
    """
    frame = inspect.currentframe()
    call_stack = inspect.getouterframes(frame, 0)
    if 1 <= n < len(call_stack):
        target_frame_info = list(reversed(list(call_stack)))[n]
        target_frame = target_frame_info.frame
        arguments = inspect.getargvalues(target_frame).locals
        try:
            if file_path is None and pkl_suffix is not None:
                file_path = "_".join([target_frame_info.function, pkl_suffix]) + ".pkl"
            elif file_path is None:
                file_path = target_frame_info.function + ".pkl"
            print("DEBUG:", n, pkl_suffix, file_path)
            with open(file_path, "wb") as f:
                pickle.dump(arguments, f)
            print(
                f"Arguments from function '{target_frame_info.function}' at stack position {n} pickled to '{file_path}'."
            )
            for arg_name, arg_value in arguments.items():
                print(f"   {arg_name} = {repr(arg_value)}")
        except Exception as e:
            print(f"Error pickling arguments: {e}")
    else:
        print(
            f"Invalid stack position: {n}. Stack depth is {len(call_stack) - 1} (excluding this console frame)."
        )


def load_pickled_args(file_path):
    """
    Loads pickled arguments from the specified file path.

    Args:
        file_path (str): The full path to the file containing the pickled data.

    Returns:
        dict or None: A dictionary containing the loaded arguments, or None if an error occurs.
    """
    try:
        with open(file_path, "rb") as f:
            loaded_args = pickle.load(f)
        return loaded_args
    except FileNotFoundError:
        print(f"Error: File not found at '{file_path}'.")
        return None
    except Exception as e:
        print(f"Error loading pickled data: {e}")
        return None


def open_console_print_stack(depth=None):
    """
    Opens an interactive Python console with access to the current scope.
    Prints the names and arguments of the calling functions.
    Includes a try-except block to prevent crashes during console initialization.
    Accesses both local and global variables.
        Args:
        depth (int): Up to stack depth (1 for the immediate caller, 2 for its caller, etc.).
    """
    if depth is not None:
        depth += 1
    frame = inspect.currentframe()
    call_stack = inspect.getouterframes(frame, 0)

    # print the stack
    print("=" * 25, " Interactive Console: Stack ", "=" * 25)
    for i, frame_info in enumerate(
        reversed(list(call_stack[1:depth]))
    ):  # Skip the current frame
        frame = frame_info.frame
        function_name = frame_info.function
        arguments = inspect.getargvalues(frame).locals

        print(f"  {i + 1}. Function: {function_name}")
        print("     Arguments:")
        for arg_name, arg_value in arguments.items():
            print(f"       {arg_name} = {repr(arg_value)}")
        print("=" * 80)

    globals_dict = frame.f_back.f_globals if frame.f_back else {}
    locals_dict = frame.f_back.f_locals if frame.f_back else {}

    # Combine locals and globals into a single dictionary for the console
    combined_scope = locals_dict.copy()
    combined_scope.update(globals_dict)

    try:
        console = code.InteractiveConsole(combined_scope)
        console.interact(
            banner="Use Ctrl+D (or quit()) to exit and resume program flow.\n Use pickle_args(n, file_path) to dump the args"
        )
    except Exception as e:
        print(f"Error initializing interactive console: {e}")


def set_trace():
    """
    calls pdb.set_trace()
    """
    pdb.set_trace()
