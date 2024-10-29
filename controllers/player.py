import os

from starlette.responses import StreamingResponse, Response

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
    tracks = [f for f in os.listdir(AUDIO_DIR) if os.path.isfile(os.path.join(AUDIO_DIR, f))]
    return {"tracks": tracks}
