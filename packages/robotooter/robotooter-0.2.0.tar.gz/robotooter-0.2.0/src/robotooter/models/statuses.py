from pathlib import Path

from pydantic import BaseModel


class RtMedia(BaseModel):
    id: str | None = None
    file_path: Path
    description: str | None = None


class RtStatus(BaseModel):
    id: str| None = None
    text: str = ''
    in_reply_to_id: str | None = None
    url: str| None = None
    media: list[RtMedia] = []
    spoiler_text: str | None = None
    quote_id: str | None = None
