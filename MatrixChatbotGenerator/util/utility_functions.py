import inspect


def current_function_name():
    return inspect.stack()[1].function
