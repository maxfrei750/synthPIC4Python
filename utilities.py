def is_iterable(obj):
    try:
        iterator = iter(obj)
    except TypeError:
        return False
    else:
        return True
