import os

from sqlalchemy import create_engine, Column, Integer, String, Numeric
from sqlalchemy.orm import sessionmaker, declarative_base

from .database import create_database_if_not_exists
from .log import add_log

LEAVE_URL = os.getenv("DATABASE_URL_LEAVE")
engine = create_engine(LEAVE_URL)
BaseLeave = declarative_base()
SessionLocal = sessionmaker(autoflush=True, bind=engine)


class Leave(BaseLeave):
    __tablename__ = "leave"
    id = Column(Integer, primary_key=True, index=True)
    telegram_id = Column(String)
    username = Column(String)
    coolname = Column(String)
    clockify_id = Column(String)
    workday = Column(String)
    hours = Column(String)
    status = Column(String)
    mode = Column(String)
    substitute = Column(String)
    description = Column(String)
    request_id = Column(Numeric)

    def __repr__(self):
        return f"(User('{self.username}') - Workday('{self.workday}') - Hour('{self.hours}') - Status('{self.status}'))"


def init_leave_db(bot):
    create_database_if_not_exists(LEAVE_URL, bot)
    try:
        BaseLeave.metadata.create_all(engine)
    except Exception as e:
        add_log(f"Error creating Leave table: {e}")


def leave_type_text(mode):
    if mode == "partremote":
        return "Part-time Remote"
    elif mode == "partvac":
        return "Part-time Absence"
    elif mode == "fullremote":
        return "Full-time Remote"
    elif mode == "fullvac":
        return "Full-time Absence"
    return "UNKNOWN"
