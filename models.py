"""
SQLAlchemy models for Licensing Roadmap
Maps to rs_* tables in shared compliance database
"""
from sqlalchemy import create_engine, Column, String, Integer, Date, Numeric, Boolean, Text, TIMESTAMP, ForeignKey, ARRAY
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker
from datetime import datetime
import uuid
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

Base = declarative_base()

class RSLicenseHolder(Base):
    __tablename__ = 'rs_license_holders'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True))
    employee_id = Column(String(50))
    full_name = Column(String(255), nullable=False)
    role = Column(String(100))
    hire_date = Column(Date)
    status = Column(String(50), default='active')
    next_target_state = Column(String(2))
    pin = Column(String(10), unique=True)
    total_licenses = Column(Integer, default=0)
    total_certificates = Column(Integer, default=0)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    deleted_at = Column(TIMESTAMP)
    
    # Relationships
    licenses = relationship("RSLicense", back_populates="holder", cascade="all, delete-orphan")
    bio_data = relationship("RSBioData", back_populates="holder", uselist=False, cascade="all, delete-orphan")

class RSLicense(Base):
    __tablename__ = 'rs_licenses'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    holder_id = Column(UUID(as_uuid=True), ForeignKey('rs_license_holders.id', ondelete='CASCADE'), nullable=False)
    license_id = Column(String(50), unique=True, nullable=False)
    jurisdiction = Column(String(100), nullable=False)
    jurisdiction_abbr = Column(String(2), nullable=False)
    jurisdiction_type = Column(String(50), nullable=False)
    license_type = Column(String(100), nullable=False)
    license_number = Column(String(100))
    status = Column(String(50), nullable=False, default='not_licensed')
    issued_on = Column(Date)
    expires_on = Column(Date)
    board_name = Column(String(255))
    board_phone = Column(String(20))
    board_email = Column(String(255))
    board_url = Column(Text)
    board_address = Column(Text)
    designated_role = Column(String(50))
    renewal_period_years = Column(Integer, default=2)
    renewal_fee = Column(Numeric(10, 2))
    continuing_ed_required = Column(Boolean, default=False)
    continuing_ed_hours = Column(Integer)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    holder = relationship("RSLicenseHolder", back_populates="licenses")
    costs = relationship("RSLicenseCost", back_populates="license", cascade="all, delete-orphan")
    budget = relationship("RSLicenseBudget", back_populates="license", uselist=False, cascade="all, delete-orphan")

class RSLicenseCost(Base):
    __tablename__ = 'rs_license_costs'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    license_id = Column(UUID(as_uuid=True), ForeignKey('rs_licenses.id', ondelete='CASCADE'), nullable=False)
    date = Column(Date, nullable=False)
    category = Column(String(50), nullable=False)
    amount = Column(Numeric(10, 2), nullable=False)
    vendor = Column(String(255))
    notes = Column(Text)
    receipt_url = Column(Text)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    
    # Relationships
    license = relationship("RSLicense", back_populates="costs")

class RSLicenseBudget(Base):
    __tablename__ = 'rs_license_budgets'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    license_id = Column(UUID(as_uuid=True), ForeignKey('rs_licenses.id', ondelete='CASCADE'), nullable=False)
    application_fee = Column(Numeric(10, 2), default=0)
    test_fee = Column(Numeric(10, 2), default=0)
    trade_book_fee = Column(Numeric(10, 2), default=0)
    business_law_book_fee = Column(Numeric(10, 2), default=0)
    activation_fee = Column(Numeric(10, 2), default=0)
    prep_course_fee = Column(Numeric(10, 2), default=0)
    travel_estimate = Column(Numeric(10, 2), default=0)
    shipping_estimate = Column(Numeric(10, 2), default=0)
    renewal_fee = Column(Numeric(10, 2), default=0)
    continuing_ed_fee = Column(Numeric(10, 2), default=0)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    license = relationship("RSLicense", back_populates="budget")

class RSCompanyCoverage(Base):
    __tablename__ = 'rs_company_coverage'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    state_code = Column(String(2), nullable=False, unique=True)
    state_name = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False, default='target')
    licensed_holders = Column(ARRAY(Text))
    primary_license_holder_id = Column(UUID(as_uuid=True), ForeignKey('rs_license_holders.id'))
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)

class RSBioData(Base):
    __tablename__ = 'rs_bio_data'
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    holder_id = Column(UUID(as_uuid=True), ForeignKey('rs_license_holders.id', ondelete='CASCADE'), nullable=False, unique=True)
    personal_info = Column(JSONB)
    addresses = Column(JSONB)
    work_history = Column(ARRAY(JSONB))
    plumbing_experience = Column(JSONB)
    job_projects = Column(ARRAY(JSONB))
    education = Column(JSONB)
    professional_references = Column(ARRAY(JSONB))
    background = Column(JSONB)
    military = Column(JSONB)
    created_at = Column(TIMESTAMP, default=datetime.utcnow)
    updated_at = Column(TIMESTAMP, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    holder = relationship("RSLicenseHolder", back_populates="bio_data")

# Database connection
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    raise ValueError("DATABASE_URL not found in environment variables")

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
