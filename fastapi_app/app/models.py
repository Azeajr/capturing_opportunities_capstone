from sqlalchemy import Column, Float, Integer, String

from app.database import Base


class ScoredPath(Base):
    __tablename__ = "scored_path"
    id = Column(Integer, primary_key=True, index=True)
    path = Column(String, unique=True, nullable=False)
    score = Column(Float, nullable=False)

    def __init__(self, path, score):
        self.path = path
        self.score = score

    def __repr__(self):
        return f"ScoredPaths('{self.image_path}', '{self.score}')"
