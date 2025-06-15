from sqlalchemy import create_engine, Column, Integer, String, Text, Date, DateTime, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func
from datetime import datetime, date
import os
from typing import Optional
from sqlalchemy import text

Base = declarative_base()

class ApplicantProfile(Base):
    __tablename__ = 'ApplicantProfile'
    
    applicant_id = Column(Integer, primary_key=True, autoincrement=True)
    first_name = Column(String(50), nullable=True)
    last_name = Column(String(50), nullable=True)
    date_of_birth = Column(Date, nullable=True)
    address = Column(String(255), nullable=True)
    phone_number = Column(String(20), nullable=True)
    
    applications = relationship("ApplicationDetail", back_populates="applicant", cascade="all, delete-orphan")
    
    def __repr__(self): 
        return f"<ApplicantProfile(id={self.applicant_id}, name='{self.first_name} {self.last_name}')>"
    
    def to_dict(self):
        return {
            'applicant_id': self.applicant_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,  # Fixed: handle None
            'address': self.address,
            'phone_number': self.phone_number
        }

class ApplicationDetail(Base):
    __tablename__ = 'ApplicationDetail'
    
    detail_id = Column(Integer, primary_key=True, autoincrement=True)
    applicant_id = Column(Integer, ForeignKey('ApplicantProfile.applicant_id'), nullable=False)
    application_role = Column(String(100), nullable=True)
    cv_path = Column(Text)
    
    applicant = relationship("ApplicantProfile", back_populates="applications")
    
    def __repr__(self):  # Fixed: double underscores
        return f"<ApplicationDetail(id={self.detail_id}, role='{self.application_role}')>"
    
    def to_dict(self):
        return {
            'detail_id': self.detail_id,
            'applicant_id': self.applicant_id,
            'application_role': self.application_role,
            'cv_path': self.cv_path
        }

class DatabaseConfig:
    def __init__(self):  # Fixed: double underscores
        self.MYSQL_HOST = os.getenv('MYSQL_HOST', 'localhost')
        self.MYSQL_PORT = os.getenv('MYSQL_PORT', '3306')
        self.MYSQL_DATABASE = os.getenv('MYSQL_DATABASE', 'ats_db')
        self.MYSQL_USER = os.getenv('MYSQL_USER', 'asepjajang')
        self.MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD', 'asepjajang123')
        
        self.DATABASE_URL = f"mysql+pymysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DATABASE}"
    
    def get_engine(self):
        return create_engine(
            self.DATABASE_URL,
            echo=False, 
            pool_pre_ping=True,
            pool_recycle=300
        )
    
    def get_session_maker(self):
        engine = self.get_engine()
        return sessionmaker(bind=engine)

def init_database():
    config = DatabaseConfig()
    engine = config.get_engine()
    Base.metadata.create_all(engine)
    return engine

def test_connection():
    config = DatabaseConfig()
    engine = config.get_engine()

    try:
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1"))
            print("Database connection successful:", list(result))
    except Exception as e:
        print("Database connection failed:", str(e))