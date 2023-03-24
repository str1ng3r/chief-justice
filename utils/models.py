from mongoengine import *

from utils.enums import CaseType


class Case(Document):
    url = StringField(required=True)
    archived = BooleanField(required=True, default=False)
    case_type = EnumField(CaseType, required=True)
    justice = BooleanField(required=True, default=False)
    name = StringField(required=True)
    handler = IntField()
    month = IntField()
    year = IntField()
