from sqlmodel import SQLModel, create_engine
import models

sqlite_file_name = "myConferences.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)


def get_session():
    with Session(engine) as session:
        yield session


def create_database():
    SQLModel.metadata.create_all(engine)


if __name__ == "__main__":
    create_database()