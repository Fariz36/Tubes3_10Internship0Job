from sqlalchemy import create_engine, Column, Integer, String, Text, Date, DateTime, Enum, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from sqlalchemy.sql import func
from datetime import datetime, date
import os
from typing import Optional

Base = declarative_base()

class ApplicantProfile(Base):
    __tablename__ = 'ApplicantProfile'
    
    applicant_id = Column(Integer, primary_key=True, autoincrement=True)
    full_name = Column(String(255), nullable=False)
    email = Column(String(255), unique=True, nullable=False, index=True)
    phone = Column(String(20))
    address = Column(Text)
    date_of_birth = Column(Date)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    applications = relationship("ApplicationDetail", back_populates="applicant", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ApplicantProfile(id={self.applicant_id}, name='{self.full_name}', email='{self.email}')>"
    
    def to_dict(self):
        return {
            'applicant_id': self.applicant_id,
            'full_name': self.full_name,
            'email': self.email,
            'phone': self.phone,
            'address': self.address,
            'date_of_birth': self.date_of_birth.isoformat() if self.date_of_birth else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class ApplicationDetail(Base):
    __tablename__ = 'ApplicationDetail'
    
    application_id = Column(Integer, primary_key=True, autoincrement=True)
    applicant_id = Column(Integer, ForeignKey('ApplicantProfile.applicant_id', ondelete='CASCADE', onupdate='CASCADE'), nullable=False, index=True)
    position = Column(String(255), nullable=False, index=True)
    company = Column(String(255), index=True)
    cv_path = Column(String(500), nullable=False, index=True)
    application_date = Column(Date, default=func.current_date())
    status = Column(Enum('pending', 'reviewed', 'shortlisted', 'rejected', 'hired', name='application_status'), default='pending', index=True)
    created_at = Column(DateTime, default=func.current_timestamp())
    updated_at = Column(DateTime, default=func.current_timestamp(), onupdate=func.current_timestamp())
    
    applicant = relationship("ApplicantProfile", back_populates="applications")
    
    def __repr__(self):
        return f"<ApplicationDetail(id={self.application_id}, position='{self.position}', status='{self.status}')>"
    
    def to_dict(self):
        return {
            'application_id': self.application_id,
            'applicant_id': self.applicant_id,
            'position': self.position,
            'company': self.company,
            'cv_path': self.cv_path,
            'application_date': self.application_date.isoformat() if self.application_date else None,
            'status': self.status,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class DatabaseConfig:
    def __init__(self):
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