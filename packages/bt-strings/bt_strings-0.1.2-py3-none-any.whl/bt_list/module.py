

def grouping(l: list|tuple, n: int) -> list|tuple[list]:
    if not isinstance(l, (list, tuple)):
        raise TypeError(f"l must be a list or tuple, instead {type(l).__name__}")
    
    return [l[i:i+n] for i in range(0, len(l), n)]