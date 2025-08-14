from pydantic import BaseModel, Field


class ReqSignCreate(BaseModel):
    paths: list[str] = Field(default_factory=list)

class RespSignCreage(BaseModel):
    path: str
    endpoint: str


class JSONResponse(BaseModel):
    code:  int
    message: str
    data: RespSignCreage


class MetaData(BaseModel):
    video_id: int = Field(alias="videoId")
    os_path: str = Field(alias="osPath")

    def get_storage_path(self) -> str:
        return self.os_path
