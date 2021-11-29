import re

def parse_symbol(line):
    res = re.search(r"\$([A-Za-z:]*)", line)
    if res is not None:
        return res.group(1).upper()
    return None 

def parse_sum(line):
    res = re.search(r"\b([0-9\.]+)USD", line)
    if res is not None and res.group(1).count('.') <= 1:
        return float(res.group(1))
    return None 
