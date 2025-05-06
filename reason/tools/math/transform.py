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


def utf8_to_int(s):
    return int.from_bytes(s.encode("utf-8"), byteorder="little")


def utf8_to_varname(s):
    return int_to_varname(utf8_to_int(s))
