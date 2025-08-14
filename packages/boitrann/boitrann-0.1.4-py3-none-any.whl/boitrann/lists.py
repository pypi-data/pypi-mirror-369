

def group(l: list|tuple, n: int = None) -> list[list|tuple]:
    if not isinstance(l, (list, tuple)):
        raise TypeError(f"l must be a list or tuple, instead {type(l).__name__}")

    n = len(l) if not n else n
    return [l[i:i+n] for i in range(0, len(l), n)]


def join(l: list|tuple[str], n: int, sep: str=',') -> str:
    if not isinstance(l, (list, tuple)):
        raise TypeError(f"l must be a list or tuple of string, instead {type(l).__name__}")
    
    if not all((isinstance(x, str)) for x in l):
        raise TypeError(f"l must be a list or tuple of string")
    
    grouping = group(l, n)
    return "\n".join(list(map(lambda x: f"{x}{sep}", [sep.join(x) for x in grouping]))).removesuffix(",")