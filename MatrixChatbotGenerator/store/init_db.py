from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base
import db_config


def init_db():
    engine = create_engine(db_config.Config.get_db_uri())
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()
    return session


if __name__ == "__main__":
    session = init_db()

    session.commit()
