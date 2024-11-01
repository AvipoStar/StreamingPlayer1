import os

from starlette.responses import StreamingResponse, Response

from config.Database import getConnection

AUDIO_DIR = "audio"


async def stream_music(filename: str):
    file_path = f"{AUDIO_DIR}/{filename}"  # Путь к вашему аудиофайлу
    if not os.path.exists(file_path):
        return Response(status_code=404)

    def audio_stream():
        with open(file_path, "rb") as audio_file:
            while chunk := audio_file.read(1024):  # Читаем файл по частям
                yield chunk

    return StreamingResponse(audio_stream(), media_type="audio/mpeg")  # Укажите правильный media_type


async def track_list():
    db = getConnection()
    cursor = db.cursor()

    # Запрос к базе данных для получения информации о треках
    query = """
    SELECT id, title, description, duration, file_url
    FROM media_items
    """

    cursor.execute(query)
    # Извлекаем все строки из результата запроса
    rows = cursor.fetchall()

    # Преобразуем результат в список словарей
    tracks = [
        {
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "duration": row[3],
            "file_url": row[4],
        }
        for row in rows
    ]

    # Закрываем соединение
    cursor.close()
    db.close()

    return {"tracks": tracks}
