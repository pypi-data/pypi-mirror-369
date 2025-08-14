def safe_get(d, *keys, default=None):
    for key in keys:
        if isinstance(d, dict) and key in d:
            d = d[key]
        else:
            return default

    if isinstance(d, dict):
        return default
    return d


def dict_merge(*dicts):
    result = {}
    for d in dicts:
        result.update(d)
    return result


def deep_merge(*dicts):
    result = {}
    for d in dicts:
        for key, value in d.items():
            if isinstance(value, dict) and key in result and isinstance(result[key], dict):
                result[key] = deep_merge(result[key], value)
            else:
                result[key] = value
    return result

