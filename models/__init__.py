from uuid import uuid4
from string import ascii_lowercase as al


def to_camel_case(field: str):
    alias = field.split('_')
    return alias[0] + ''.join(i.title() for i in alias[1:])


def random_id(r=0):
    return uuid4().fields[r]


def ref_id():
    c = random_id()
    return ''.join(al[int(i)] for i in str(c))[0:8]
