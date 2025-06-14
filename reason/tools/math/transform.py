def int_to_varname(n):
    if n == 0:
        return "0"
    digits = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
    base = len(digits)
    result = ""
    n = abs(n)
    while n:
        result = digits[n % base] + result
        n //= base
    return result

def varname_to_int(s):
    if s == "0":
        return 0
    digits = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
    base = len(digits)
    value = 0
    for char in s:
        value = value * base + digits.index(char)
    return value


def utf8_to_int(s):
    return int.from_bytes(s.encode("utf-8"), byteorder="little")


def utf8_to_varname(s):
    return int_to_varname(utf8_to_int(s))


def int_to_uft8(n):
    length = (n.bit_length() + 7) // 8  
    return n.to_bytes(length, byteorder="little").decode("utf-8")

def varname_to_utf8(s):
    return int_to_uft8(varname_to_int(s))


