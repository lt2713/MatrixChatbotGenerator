from sqlalchemy import create_engine
from store.models import Base
from store import db_config


def recreate_db():
    engine = create_engine(db_config.Config.get_db_uri())
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)


def main():
    recreate_db()


if __name__ == "__main__":
    main()


