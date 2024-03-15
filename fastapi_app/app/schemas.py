from pydantic import BaseModel


class ScoredPathBase(BaseModel):
    path: str
    score: float


class ScoredPathCreate(ScoredPathBase):
    pass


class ScoredPath(ScoredPathBase):
    id: int

    class Config:
        orm_mode = True
