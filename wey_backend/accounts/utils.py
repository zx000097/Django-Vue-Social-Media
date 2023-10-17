def get_dict_values_string(dict) -> str:
    return " ".join([" ".join(x for x in l) for l in list(dict.values())])
