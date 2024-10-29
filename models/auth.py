from MySQLdb.times import Date
from pydantic import BaseModel


class LoginClass(BaseModel):
    email: str
    password: str


class RegistrationClass(BaseModel):
    email: str
    password: str
    surname: str
    name: str
    patronymic: str
    bornDate: Date
