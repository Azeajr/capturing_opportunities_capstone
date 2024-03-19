from cap_opp import db


class ScoredPath(db.Model):
    __tablename__ = "scored_path"
    id = db.Column(db.Integer, primary_key=True)
    path = db.Column(db.String(255), unique=True, nullable=False)
    score = db.Column(db.Float, nullable=False)

    def __init__(self, path, score):
        self.path = path
        self.score = score

    def __repr__(self):
        return f"ScoredPaths('{self.image_path}', '{self.score}')"


# from sqlalchemy import Column, Integer, String, Float

# from cap_opp.database import Base


# class ScoredPaths(Base):
#     __tablename__ = "scored_paths"
#     id = Column(Integer, primary_key=True)
#     image_path = Column(String(100), nullable=False)
#     score = Column(Float, nullable=False)

#     def __init__(self, image_path, score):
#         self.image_path = image_path
#         self.score = score

#     def __repr__(self):
#         return f"ScoredPaths('{self.image_path}', '{self.score}')"
