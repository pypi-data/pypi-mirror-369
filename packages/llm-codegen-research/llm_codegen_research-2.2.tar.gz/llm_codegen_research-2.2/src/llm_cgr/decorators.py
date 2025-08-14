"""Useful decorators for research methods."""

import traceback
from datetime import datetime


def experiment(function):
    """Decorator to mark a function as an experiment."""

    def wrapper(*args, **kwargs):
        try:
            print(
                "\n"
                "===== STARTING EXPERIMENT "
                f"== {function.__name__} "
                f"== {datetime.now().isoformat()} ====="
            )
            result = function(*args, **kwargs)
            print(
                "===== FINISHED EXPERIMENT "
                f"== {function.__name__} "
                f"== {datetime.now().isoformat()} ====="
                "\n"
            )
            return result

        except Exception as e:
            trace = traceback.format_exception(type(e), value=e, tb=e.__traceback__)
            print("".join(trace))
            print(
                "===== EXPERIMENT FAILED "
                f"== {function.__name__} "
                f"== {datetime.now().isoformat()} ====="
            )
            return None

    return wrapper
