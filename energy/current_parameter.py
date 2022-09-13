def current_parameter(plc):
    if plc == 40 or plc == 41 or plc == 53 or plc == 54 or plc == 56:
        current_factor = [10, 10]
    else:
        current_factor = [100, 5]
    return current_factor