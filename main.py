from fastapi import FastAPI, Response
from fastapi.responses import StreamingResponse
import os

from starlette.middleware.cors import CORSMiddleware
from routers.auth import router as auth_router
from routers.player import router as player_router

app = FastAPI()

AUDIO_DIR = "audio"

# Добавляем middleware для обработки CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Здесь можно указать список допустимых источников запросов
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем все HTTP методы
    allow_headers=["*"],  # Разрешаем все заголовки
)

app.include_router(
    router=auth_router,
    prefix='/auth'
)

app.include_router(
    router=player_router,
    prefix='/player'
)
