from fastapi import APIRouter

from controllers.player import stream_music, track_list

router = APIRouter()


@router.get("/audio/{filename}", tags=["Player"])
async def stream_audio(filename: str):
    streaming_response = await stream_music(filename)
    return streaming_response


@router.get("/tracks", tags=["Player"])
async def list_tracks():
    tracks = await track_list()
    return tracks
