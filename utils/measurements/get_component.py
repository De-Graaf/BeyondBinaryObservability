def get_component(input_data, ctype, default=None):
    """
    Return the array for a given ComponentType, working for both
    enum-keyed and string-keyed dicts.
    """
    if default is None:
        default = []

    if not isinstance(input_data, dict):
        return default

    # 1) Enum key
    if ctype in input_data:
        return input_data[ctype]

    # 2) Value string, e.g. 'sym_power_sensor'
    val = getattr(ctype, "value", None)
    if val is not None and val in input_data:
        return input_data[val]

    # 3) Name string, e.g. 'sym_power_sensor'
    name = getattr(ctype, "name", None)
    if name is not None and name in input_data:
        return input_data[name]

    return default