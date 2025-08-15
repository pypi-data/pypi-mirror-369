from functools import wraps


def decorate_all_methods(decorator: callable, exclude=None, exclude_startswith: str = None):
    if exclude is None:
        exclude = []

    def decorate(cls):
        for attr, value in cls.__dict__.items():
            if callable(value) \
                    and attr not in exclude \
                    and (not exclude_startswith or not attr.startswith(exclude_startswith)):
                @wraps(value)
                def wrapped_func(*args, _value=value, **kwargs):
                    return decorator(_value)(*args, **kwargs)

                setattr(cls, attr, wrapped_func)

        return cls

    return decorate
