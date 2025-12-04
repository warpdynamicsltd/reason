VAR_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"

def int_to_varname(n):
    if n == 0:
        return "0"
    digits = VAR_CHARS
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
    digits = VAR_CHARS
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


def str_to_var(s):
    """Convert arbitrary string to valid variable name.

    Encoding:
    - Alphanumeric characters (a-z, A-Z, 0-9) stay as is
    - Underscore (_) is encoded as __
    - All other characters are encoded as _u<hex>_ where hex is:
      - 2 digits (1 byte) for code points 0x00-0xFF
      - 4 digits (2 bytes) for code points 0x100-0xFFFF
      - 8 digits (4 bytes) for code points >= 0x10000

    Examples:
        >>> str_to_var("hello_world")
        'hello__world'
        >>> str_to_var("hello world!")
        'hello_u20_world_u21_'
        >>> str_to_var("test@email.com")
        'test_u40_email_u2e_com'
    """
    result = []
    for char in s:
        if char.isalnum():
            result.append(char)
        elif char == '_':
            result.append('__')
        else:
            code_point = ord(char)
            if code_point <= 0xFF:
                result.append(f'_u{code_point:02x}_')
            elif code_point <= 0xFFFF:
                result.append(f'_u{code_point:04x}_')
            else:
                result.append(f'_u{code_point:08x}_')
    return ''.join(result)


def var_to_str(var_name):
    """Convert variable name back to original string.

    Inverse of str_to_var. Decodes the encoded variable name back to the
    original string.

    Examples:
        >>> var_to_str("hello__world")
        'hello_world'
        >>> var_to_str("hello_u20_world_u21_")
        'hello world!'
        >>> var_to_str("test_u40_email_u2e_com")
        'test@email.com'
    """
    result = []
    i = 0
    while i < len(var_name):
        if var_name[i] == '_':
            if i + 1 < len(var_name):
                if var_name[i + 1] == '_':
                    # Double underscore -> single underscore
                    result.append('_')
                    i += 2
                elif var_name[i + 1] == 'u':
                    # Encoded character: _u<hex>_
                    # Find the closing underscore
                    end = var_name.find('_', i + 2)
                    if end == -1:
                        raise ValueError(f"Invalid encoding: no closing underscore found after position {i}")
                    hex_str = var_name[i + 2:end]
                    code_point = int(hex_str, 16)
                    result.append(chr(code_point))
                    i = end + 1
                else:
                    raise ValueError(f"Invalid encoding at position {i}: expected '_' or 'u' after '_'")
            else:
                raise ValueError(f"Invalid encoding: trailing underscore at position {i}")
        else:
            # Regular alphanumeric character
            result.append(var_name[i])
            i += 1
    return ''.join(result)
