import jwt
import hashlib
from fastapi import FastAPI, HTTPException, status
from config.Database import getConnection
from models.auth import RegistrationClass

app = FastAPI()

SECRET_KEY = "your-secret-key"  # Поменяйте на более сложный и защитите его
ALGORITHM = "HS256"


def hash_password(password: str) -> str:
    """Хэширует пароль с использованием SHA-256."""
    return hashlib.sha256(password.encode()).hexdigest()


def register_user(registration_data: RegistrationClass):
    db = getConnection()
    cursor = db.cursor()

    try:
        # Проверка на существование пользователя с таким же email
        cursor.execute("SELECT id FROM users WHERE email = %s", (registration_data.email,))
        result = cursor.fetchone()
        if result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Пользователь с таким email уже существует"
            )

        # Хэширование пароля на Python стороне
        hashed_password = hash_password(registration_data.password)

        # Добавление нового пользователя
        cursor.execute(
            """
            INSERT INTO users (email, password, surname, name, patronymic, bornDate)
            VALUES (%s, %s, %s, %s, %s, %s)
            """,
            (
                registration_data.email,
                hashed_password,
                registration_data.surname,
                registration_data.name,
                registration_data.patronymic,
                registration_data.bornDate
            )
        )
        db.commit()
        user_id = cursor.lastrowid

    finally:
        cursor.close()
        db.close()

    # Создание access_token для нового пользователя
    access_token = createAccessToken(
        data={"sub": registration_data.email, "id": user_id}
    )

    return {
        "user_id": user_id,
        "access_token": access_token
    }


def createAccessToken(data: dict):
    to_encode = data.copy()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def login(email: str, password: str):
    db = getConnection()
    cursor = db.cursor()

    try:
        # Проверка пользователя с таким email
        cursor.execute("SELECT id, password, surname, name FROM users WHERE email = %s", (email,))
        result = cursor.fetchone()

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        user_id, db_password, surname, name = result

        # Хэширование введённого пароля и проверка
        hashed_password = hash_password(password)
        if db_password != hashed_password:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный пароль"
            )

    finally:
        cursor.close()
        db.close()

    # Создание токена
    access_token = createAccessToken(
        data={"sub": email, "id": user_id}
    )

    return {
        "user_id": user_id,
        "access_token": access_token
    }


def loginToken(token: str):
    try:
        # Декодирование токена
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("id")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный токен"
            )

        # Если токен действителен, возвращаем подтверждение
        return {"message": "Токен действителен", "user_id": user_id}

    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Срок действия токена истек"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен"
        )


def getUserDetails(user_id: int):
    db = getConnection()
    cursor = db.cursor()

    try:
        # Запрос к базе данных для получения данных пользователя по user_id
        cursor.execute("SELECT surname, name, patronymic, bornDate FROM users WHERE id = %s", (user_id,))
        result = cursor.fetchone()

        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Пользователь не найден"
            )

        surname, name, patronymic, bornDate = result

        return {
            "surname": surname,
            "name": name,
            "patronymic": patronymic,
            "bornDate": bornDate
        }

    finally:
        cursor.close()
        db.close()
