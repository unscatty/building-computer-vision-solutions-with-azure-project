from types import SimpleNamespace
class NestedNamespace(SimpleNamespace):
    def __init__(self, dictionary, **kwargs):
        super().__init__(**kwargs)
        for key, value in dictionary.items():
            if isinstance(value, dict):
                self.__setattr__(key, NestedNamespace(value))
            else:
                self.__setattr__(key, value)

def __dict_fetch(dictionary: dict, key, to_dict=True, raises=False) -> dict:
    if dictionary is None:
        return

    __dict = dictionary

    if not isinstance(__dict, dict):
        if to_dict:
            if hasattr(__dict, 'to_dict'):
                __dict = dictionary.to_dict()
            elif isinstance(__dict, list):
                # Transform list to dict
                return [__dict_fetch(item, key, to_dict, raises) for item in __dict]
            elif raises:
                raise TypeError(
                    f'Object with key {key} is of type <{type(__dict)}>, and cannot be transformed to <dict>')
            else:
                return
        else:
            return

    if isinstance(key, list):
        return {key_key: key_val for k in key for key_key, key_val in __dict_fetch(__dict, k, to_dict, raises).items()}

    if isinstance(key, dict):
        return {k: __dict_fetch(__dict.get(k), v, to_dict, raises) if __dict else None for k, v in key.items()}

    else:
        return {key: __dict.get(key)}

partial_dict = __dict_fetch

def list_to_dict(lst: list) -> dict:
    return dict(enumerate(lst))

def to_dict(obj, recursive=True) -> dict:
    if recursive:
        if isinstance(obj, dict):
            return {key: to_dict(val, True) for key, val in obj.items()}
    
        if isinstance(obj, list):
            return [to_dict(item, True) for item in obj]

        if hasattr(obj, 'to_dict'):
            return to_dict(obj.to_dict())
        
        if hasattr(obj, '__dict__'):
            return to_dict(obj.__dict__)

    if hasattr(obj, 'to_dict'):
        return obj.to_dict()
    
    if hasattr(obj, '__dict__'):
        return obj.__dict__
    
    return obj
