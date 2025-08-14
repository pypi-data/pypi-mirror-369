

def join(l: list|tuple[str], n: int, sep: str) -> str:
    if not isinstance(l, (list, tuple)):
        raise TypeError(f"l must be a list or tuple of string, instead {type(l).__name__}")
    
    if not all((isinstance(x, str)) for x in l):
        raise TypeError(f"l must be a list or tuple of string")
        
    return "\n".join([sep.join(l[i:i+n]) for i in range(0, len(l), n)])


