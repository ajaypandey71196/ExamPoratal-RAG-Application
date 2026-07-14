"""Database ORM Models."""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import uuid

from app.database import Base


class User(Base):
    """User model."""
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, nullable=False, index=True)
    username = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    first_name = Column(String(100))
    last_name = Column(String(100))
    profile_picture_url = Column(String(500))
    bio = Column(Text)
    role = Column(String(50), default="user")
    subscription_tier = Column(String(50), default="free")
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)

    # Relationships
    documents = relationship("Document", back_populates="user", cascade="all, delete-orphan")
    exams = relationship("Exam", back_populates="user", cascade="all, delete-orphan")
    settings = relationship("UserSettings", back_populates="user", uselist=False, cascade="all, delete-orphan")


class UserSettings(Base):
    """User settings and API keys model."""
    __tablename__ = "user_settings"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    default_llm_provider = Column(String(50))
    default_llm_model = Column(String(100))
    default_temperature = Column(Float, default=0.7)
    default_max_tokens = Column(Integer, default=1024)
    documents_quota_mb = Column(Integer, default=500)
    monthly_api_calls_quota = Column(Integer, default=10000)
    custom_prompt_template = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="settings")


class Document(Base):
    """Document model."""
    __tablename__ = "documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    file_name = Column(String(500), nullable=False)
    file_path = Column(String(1000))
    file_type = Column(String(20))
    file_size_bytes = Column(Integer)
    title = Column(String(500))
    description = Column(Text)
    processing_status = Column(String(50), default="pending")
    error_message = Column(Text)
    total_chunks = Column(Integer, default=0)
    embedding_status = Column(String(50), default="pending")
    is_public = Column(Boolean, default=False)
    tags = Column(String(500))
    upload_date = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="documents")
    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    """Document chunks model."""
    __tablename__ = "document_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"), nullable=False, index=True)
    chunk_index = Column(Integer, nullable=False)
    chunk_text = Column(Text, nullable=False)
    qdrant_vector_id = Column(UUID(as_uuid=True), nullable=False)
    chunk_start_page = Column(Integer)
    chunk_start_char = Column(Integer)
    chunk_end_char = Column(Integer)
    tokens_count = Column(Integer)
    embedding_model = Column(String(100), default="all-MiniLM-L6-v2")
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    document = relationship("Document", back_populates="chunks")


class Exam(Base):
    """Exam model."""
    __tablename__ = "exams"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(500), nullable=False)
    topic = Column(String(255), nullable=False)
    description = Column(Text)
    question_type = Column(String(100))
    difficulty_level = Column(String(50))
    num_questions = Column(Integer, nullable=False)
    time_duration_minutes = Column(Integer)
    source_preference = Column(String(100))
    used_documents = Column(JSON)
    used_sources = Column(JSON)
    custom_instructions = Column(Text)
    llm_provider = Column(String(50))
    llm_model = Column(String(100))
    generation_duration_seconds = Column(Integer)
    prompt_used = Column(Text)
    is_published = Column(Boolean, default=False)
    is_shared = Column(Boolean, default=False)
    shared_link_token = Column(String(255), unique=True)
    shared_link_expiry = Column(DateTime)
    is_deleted = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    generation_timestamp = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="exams")
    questions = relationship("ExamQuestion", back_populates="exam", cascade="all, delete-orphan")


class ExamQuestion(Base):
    """Exam questions model."""
    __tablename__ = "exam_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    exam_id = Column(UUID(as_uuid=True), ForeignKey("exams.id", ondelete="CASCADE"), nullable=False, index=True)
    question_number = Column(Integer, nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50))
    difficulty_level = Column(String(50))
    options = Column(JSON)
    correct_answer = Column(String(50))
    explanation = Column(Text)
    key_concepts = Column(String(500))
    difficulty_score = Column(Float)
    source_id = Column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="SET NULL"))
    source_type = Column(String(50))
    source_url = Column(String(1000))
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    exam = relationship("Exam", back_populates="questions")
