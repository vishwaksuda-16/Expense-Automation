from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/expense_db")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    employee = Column(String(100), nullable=False)
    amount = Column(Float, nullable=False)
    submitted_category = Column(String(100), nullable=False)   # what employee said
    ai_category = Column(String(100), nullable=True)           # what AI determined
    description = Column(Text, nullable=False)
    receipt_ref = Column(String(200), nullable=True)

    risk_flag = Column(String(50), nullable=True)              # low / medium / high
    risk_reason = Column(Text, nullable=True)
    approval_level = Column(String(50), nullable=True)         # auto / manager / director / finance_review
    status = Column(String(50), default="pending")             # pending / approved / flagged / rejected

    ai_notes = Column(Text, nullable=True)                     # full AI reasoning
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    Base.metadata.create_all(bind=engine)