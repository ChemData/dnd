
def to_numeric_cr(cr: str):
    cr = str(cr)
    try:
        return float(cr)
    except ValueError:
        num, denom = cr.split('/')
        return float(num) / float(denom)
