from fastapi import APIRouter

from controllers.auth import login, loginToken, register_user, getUserDetails
from models.auth import LoginClass, RegistrationClass

router = APIRouter()


@router.post('/login', tags=["Auth"])
def auth(loginData: LoginClass):
    user = login(loginData.email, loginData.password)
    return user


@router.post('/loginToken', tags=["Auth"])
def auth_token(token: str):
    user = loginToken(token)
    return user


@router.post('/register', tags=["Auth"])
def auth(registrationData: RegistrationClass):
    user = register_user(registrationData)
    return user

@router.get('/getUserData/{userId}', tags=["Auth"])
def auth(userId: int):
    userData = getUserDetails(userId)
    return userData
