from sqlalchemy.orm import Session

from app import models, schemas


def create_scored_path(db: Session, scored_path: schemas.ScoredPathCreate):
    db_scored_path = models.ScoredPath(path=scored_path.path, score=scored_path.score)
    db.add(db_scored_path)
    db.commit()
    db.refresh(db_scored_path)
    return db_scored_path

def read_scored_path(db: Session, scored_path_id: int):
    return db.query(models.ScoredPath).filter(models.ScoredPath.id == scored_path_id).first()


def read_scored_paths(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.ScoredPath).offset(skip).limit(limit).all()
