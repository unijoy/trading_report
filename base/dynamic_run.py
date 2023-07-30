import importlib
import os
import inspect


def dynamic_funcs(data, dir_path='adapter'):
    """
    dynamic call functions in `dir_path`,the function which start with 'html_' todo hard code
    :param data: the dynamic function's parameters
    :param dir_path: dynamic function's location
    :return:
    """
    func_list = []
    # Loop through all files in directory
    for filename in os.listdir(dir_path):
        # Check if file is a Python file
        if filename.endswith(".py"):
            # Import module using filename (without .py extension) as module name
            module_name = filename[:-3]
            module = importlib.import_module(f"{dir_path}.{module_name}")

            # Loop through all functions in module and call them
            for func_name, func in inspect.getmembers(module, inspect.isfunction):
                if func_name.startswith("html_"):
                    print("@dynamic funcs:", func_name)
                    func_list.append(func)
                    # res, title = func(**data)
                    # result[f'{title}_{func_name}'] = res

    result = _call_functions(func_list, data)
    return result


def _call_functions(func_list, data):
    """
    This function takes a list of functions to be called and manages their execution order,
    ensuring that any function which requires an argument that is not yet available is moved
    to the end of the list for later processing.
    """
    result = {}  # html result
    arg_dict = data  # A dictionary to store the arguments for each function
    while func_list:
        func = func_list.pop(0)
        args = []  # A list to store the arguments for this function
        for arg in inspect.signature(func).parameters:
            # Check if the argument is already available in the arg_dict
            if arg in arg_dict:
                args.append(arg_dict[arg])
            else:
                # Argument not available, move this function to the end of the list
                func_list.append(func)
                print("function:", func.__name__," waitting ")
                break
        else:
            # All arguments are available, call the function and store its result in the arg_dict
            print("-------------------  start  -------------------")
            print("function:", func.__name__)
            html, title, para = func(*args)  # para call be used in later function call 调用func后得到的数据，供后续func使用
            print("-------------------   end   -------------------")
            if para is not None:
                arg_dict.update(para)
            result[f'{title} - {func.__name__}'] = html
    # All functions have been called, return the final results
    return result


if __name__ == '__main__':
    dynamic_funcs(None)
