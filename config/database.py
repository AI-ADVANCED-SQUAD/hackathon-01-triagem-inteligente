from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from config.settings import DATABASE_URL

Base = declarative_base()


class Database:
    def __init__(self):
        self.db_url = DATABASE_URL
        self.engine = create_engine(self.db_url, echo=True)
        self._SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def create_tables(self):
        Base.metadata.create_all(bind=self.engine)

    def get_session(self):
        return self._SessionLocal()
