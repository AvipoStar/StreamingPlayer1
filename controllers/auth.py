import jwt
import mysql.connector
from fastapi import FastAPI, HTTPException, status

from models.auth import RegistrationClass

app = FastAPI()

SECRET_KEY = "Балто"
ALGORITHM = "HS256"


def register_user(registration_data: RegistrationClass):
    # Подключение к базе данных
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="streamingplaer"
    )
    cursor = db.cursor()

    # Проверка на существование пользователя с таким же email
    cursor.execute("SELECT id FROM users WHERE email = %s", (registration_data.email,))
    result = cursor.fetchone()
    if result:
        db.close()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Пользователь с таким email уже существует"
        )
    # Добавление нового пользователя
    cursor.execute(
        """
        INSERT INTO users (email, password, surname, name, patronymic, bornDate)
        VALUES (%s, SHA2(HEX(%s), 256), %s, %s, %s, %s)
        """,
        (
            registration_data.email,
            registration_data.password,
            registration_data.surname,
            registration_data.name,
            registration_data.patronymic,
            registration_data.bornDate
        )
    )
    db.commit()
    user_id = cursor.lastrowid
    db.close()

    # Создание access_token для нового пользователя
    access_token = createAccessToken(
        data={"sub": registration_data.email, "id": user_id})

    return {
        "user_id": user_id,
        "access_token": access_token
    }


def createAccessToken(data: dict):
    # Копируем данные, чтобы избежать их модификации
    to_encode = data.copy()

    # Генерируем JWT-токен без истечения срока действия
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


# Функция для проверки учетных данных и генерации токена
def login(email: str, password: str):
    # Подключение к базе данных
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="streamingplaer"
    )
    cursor = db.cursor()

    # Проверка пользователя с таким email
    cursor.execute("SELECT id, password, surname, name FROM users WHERE email = %s", (email,))
    result = cursor.fetchone()

    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    user_id, db_password, surname, name = result

    # Проверка пароля
    cursor.execute("SELECT SHA2(HEX(%s), 256)", (password,))
    hex_password = cursor.fetchone()[0]
    if db_password != hex_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный пароль"
        )

    # Создание токена
    access_token = createAccessToken(
        data={"sub": email, "id": user_id}
    )

    return {
        "user_id": user_id,
        "access_token": access_token
    }


# Функция для проверки существующего токена
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
    # Подключение к базе данных
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="streamingplaer"
    )
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
        cursor.close()  # Закрытие курсора
        db.close()  # Закрытие соединения
