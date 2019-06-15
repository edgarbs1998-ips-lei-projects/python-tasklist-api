from datetime import datetime


def datetime_json(o):
    if isinstance(o, datetime):
        return o.__str__()
