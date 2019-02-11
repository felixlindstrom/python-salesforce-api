import distutils.util


def parse_bool(input_value: str) -> bool:
    return distutils.util.strtobool(input_value)
