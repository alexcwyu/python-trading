import numpy as np
import pandas as pd
def representableAsInt(s: str):
    try:
        int(s)
        return True
    except ValueError:
        return False


def to_int(val, default=np.NAN):
    if representableAsInt(val):
        return int(int)
    else:
        return default