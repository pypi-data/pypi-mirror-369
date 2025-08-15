def parse_resolution(string):

    try:
        string_to_tuple = tuple(int(val) for val in string.lower().split('x'))
    except:
        raise Exception('Invalid Resolution!')

    return tuple((string_to_tuple[0], string_to_tuple[1]))


def parse_mb(string):

    if 'MB' in str(string).upper():
        string_to_mb = int(float(string[:-2]) * 1024 * 1024)
    else:
        string_to_mb = int(string)

    return string_to_mb

