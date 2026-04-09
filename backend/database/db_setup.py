"""
Database Setup Module
======================
SQLAlchemy ORM models and database initialization.
Expanded schema supporting multi-stakeholder platform.
"""

from sqlalchemy import (
    create_engine, Column, Integer, String, Float, Text,
    DateTime, Boolean, ForeignKey, JSON
)
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
DATABASE_URL = f"sqlite:///{BASE_DIR / 'skillgap.db'}"

engine = create_engine(DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


# ====================================
# USER PROFILES
# ====================================
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    email = Column(String(150), unique=True, nullable=True)
    role = Column(String(50), default="student")  # student, college, recruiter, institute
    experience_years = Column(Float, default=0)
    target_role = Column(String(100), nullable=True)
    region = Column(String(50), default="India")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    skills = relationship("UserSkill", back_populates="user", cascade="all, delete-orphan")
    analyses = relationship("AnalysisHistory", back_populates="user", cascade="all, delete-orphan")


# ====================================
# SKILLS MASTER TABLE
# ====================================
class Skill(Base):
    __tablename__ = "skills"

    id = Column(Integer, primary_key=True, index=True)
    canonical_name = Column(String(100), unique=True, nullable=False)
    category = Column(String(50), nullable=False)
    subcategory = Column(String(50), nullable=True)
    difficulty = Column(String(20), default="intermediate")
    market_weight = Column(Float, default=5.0)
    estimated_hours = Column(Integer, default=40)
    onet_code = Column(String(20), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ====================================
# USER SKILLS (Many-to-Many)
# ====================================
class UserSkill(Base):
    __tablename__ = "user_skills"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    skill_name = Column(String(100), nullable=False)
    proficiency_level = Column(String(20), default="intermediate")  # beginner/intermediate/advanced
    years_experience = Column(Float, default=0)

    user = relationship("User", back_populates="skills")


# ====================================
# JOB LISTINGS
# ====================================
class JobListing(Base):
    __tablename__ = "job_listings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200), nullable=False)
    company = Column(String(100), nullable=True)
    region = Column(String(50), nullable=True)
    skills_required = Column(Text, nullable=True)  # pipe-separated
    experience_required = Column(Float, default=0)
    salary_estimate = Column(Float, nullable=True)
    source = Column(String(50), default="simulated")
    posted_date = Column(DateTime, default=datetime.utcnow)
    scraped_at = Column(DateTime, default=datetime.utcnow)


# ====================================
# ANALYSIS HISTORY
# ====================================
class AnalysisHistory(Base):
    __tablename__ = "analysis_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    resume_skills = Column(Text, nullable=True)  # JSON
    job_skills = Column(Text, nullable=True)  # JSON
    match_percentage = Column(Float, default=0)
    employability_score = Column(Float, default=0)
    readiness_level = Column(String(30), nullable=True)
    gap_severity = Column(String(20), nullable=True)
    missing_skills = Column(Text, nullable=True)  # JSON
    analysis_result = Column(Text, nullable=True)  # Full JSON result
    created_at = Column(DateTime, default=datetime.utcnow)

    user = relationship("User", back_populates="analyses")


# ====================================
# MARKET TRENDS
# ====================================
class MarketTrend(Base):
    __tablename__ = "market_trends"

    id = Column(Integer, primary_key=True, index=True)
    skill_name = Column(String(100), nullable=False)
    demand_score = Column(Float, default=0)
    region = Column(String(50), default="Global")
    recorded_date = Column(DateTime, default=datetime.utcnow)


# ====================================
# LEARNING PATHS
# ====================================
class LearningPath(Base):
    __tablename__ = "learning_paths"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    target_role = Column(String(100), nullable=True)
    path_data = Column(Text, nullable=True)  # JSON
    total_hours = Column(Integer, default=0)
    total_skills = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)


# ====================================
# SKILL CATEGORIES
# ====================================
class SkillCategory(Base):
    __tablename__ = "skill_categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    display_name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    skill_count = Column(Integer, default=0)


# ====================================
# CREATE ALL TABLES
# ====================================
def init_db():
    """Initialize database and create all tables."""
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully!")


def get_db():
    """Get database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Initialize on import
init_db()