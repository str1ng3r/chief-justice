from mongoengine import *

from utils.enums import CaseType


class Case(Document):
    url = StringField(required=True)
    archived = BooleanField(required=True)
    case_type = EnumField(CaseType, required=True)
    justice = BooleanField(required=True)
    name = StringField(required=True)
    handler = IntField()
    month = IntField()
    year = IntField()


class Reminder(Document):
    user_id = IntField(required=True)
    reminder_date = IntField(required=True)
    reminder_text = StringField(required=True)
