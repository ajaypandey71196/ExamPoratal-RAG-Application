"""Exam API endpoints."""

import logging
import json
from uuid import UUID
from datetime import datetime
from typing import Optional, List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from pydantic import BaseModel

from app.database import get_db
from app.models import Exam, ExamQuestion, Document
from app.utils.security import get_current_user_id
from app.services.rag_engine import RAGEngine
from app.services.exam_generator import ExamGenerationService
from app.services.llm_service import LLMService
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()


# Pydantic models for request/response
class LLMConfig(BaseModel):
    """LLM configuration."""
    provider: str  # "openai", "cohere", "huggingface", "ollama"
    model: str
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 2000


class ExamGenerationRequest(BaseModel):
    """Exam generation request."""
    topic: str
    num_questions: int = 10
    question_type: str = "MCQ"  # MCQ, SHORT_ANSWER, ESSAY, MIXED
    difficulty_level: str = "medium"  # easy, medium, hard, mixed
    document_ids: Optional[List[str]] = None  # Specific documents to use
    custom_instructions: Optional[str] = None
    llm_config: LLMConfig
    source_preference: str = "documents"  # "documents", "internet", "both"


class ExamQuestionResponse(BaseModel):
    """Exam question response."""
    question_number: int
    question_text: str
    question_type: str
    difficulty_level: str
    options: Optional[dict] = None
    correct_answer: str
    explanation: str
    key_concepts: Optional[str] = None


class ExamGenerationResponse(BaseModel):
    """Exam generation response."""
    exam_id: str
    title: str
    topic: str
    num_questions: int
    question_type: str
    difficulty_level: str
    questions: List[ExamQuestionResponse]
    sources: List[dict]
    generation_duration_seconds: float
    status: str


@router.post("/generate")
async def generate_exam(
    request: ExamGenerationRequest,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """Generate a new exam based on topic and user preferences."""
    try:
        start_time = datetime.utcnow()
        
        logger.info(f"Generating exam for user {user_id}, topic: {request.topic}")

        # Validate LLM config
        if not request.llm_config.api_key and request.llm_config.provider != "ollama":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"API key required for provider {request.llm_config.provider}"
            )

        # Get documents if specific IDs provided
        documents_filter = []
        if request.document_ids:
            result = await db.execute(
                select(Document).where(
                    (Document.id.in_([UUID(doc_id) for doc_id in request.document_ids])) &
                    (Document.user_id == UUID(user_id)) &
                    (Document.processing_status == "completed")
                )
            )
            documents_filter = result.scalars().all()
            if not documents_filter:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="No valid processed documents found with provided IDs"
                )
        else:
            # Get all user's documents
            result = await db.execute(
                select(Document).where(
                    (Document.user_id == UUID(user_id)) &
                    (Document.processing_status == "completed")
                )
            )
            documents_filter = result.scalars().all()

        document_ids = [str(doc.id) for doc in documents_filter]
        
        if not document_ids and request.source_preference in ["documents", "both"]:
            logger.warning(f"No documents available for user {user_id}")

        # Initialize RAG Engine
        rag_engine = RAGEngine(
            embeddings_service=None,  # Will be initialized inside RAG engine
            qdrant_service=None  # Will be initialized inside RAG engine
        )

        # Retrieve context
        context = rag_engine.retrieve_context(
            query=request.topic,
            user_id=user_id,
            limit=20,
            source_types=["document"] if request.source_preference == "documents" else None
        )

        logger.info(f"Retrieved {len(context['chunks'])} context chunks for exam generation")

        # Initialize LLM Service
        llm_service = LLMService(
            provider=request.llm_config.provider,
            api_key=request.llm_config.api_key,
            model=request.llm_config.model
        )

        # Initialize Exam Generator
        exam_generator = ExamGenerationService(llm_service=llm_service)

        # Generate exam
        exam_data = exam_generator.generate_exam(
            topic=request.topic,
            context_chunks=context['chunks'],
            num_questions=request.num_questions,
            question_type=request.question_type,
            difficulty_level=request.difficulty_level,
            custom_instructions=request.custom_instructions,
            temperature=request.llm_config.temperature,
            max_tokens=request.llm_config.max_tokens
        )

        if not exam_data or "questions" not in exam_data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate exam questions"
            )

        # Save exam to database
        exam = Exam(
            user_id=UUID(user_id),
            title=f"Exam: {request.topic}",
            topic=request.topic,
            question_type=request.question_type,
            difficulty_level=request.difficulty_level,
            num_questions=request.num_questions,
            source_preference=request.source_preference,
            used_documents=document_ids,
            used_sources=json.dumps(context.get('sources', [])),
            custom_instructions=request.custom_instructions,
            llm_provider=request.llm_config.provider,
            llm_model=request.llm_config.model,
            prompt_used=exam_data.get("prompt_used", "")
        )

        db.add(exam)
        await db.flush()  # Get exam ID

        # Save questions
        question_records = []
        for idx, question in enumerate(exam_data.get("questions", []), 1):
            q = ExamQuestion(
                exam_id=exam.id,
                question_number=idx,
                question_text=question.get("question", ""),
                question_type=question.get("type", request.question_type),
                difficulty_level=question.get("difficulty", request.difficulty_level),
                options=question.get("options"),
                correct_answer=question.get("answer", ""),
                explanation=question.get("explanation", ""),
                key_concepts=question.get("concepts"),
                source_type="document"
            )
            question_records.append(q)

        db.add_all(question_records)

        # Calculate generation duration
        end_time = datetime.utcnow()
        generation_duration = (end_time - start_time).total_seconds()
        exam.generation_duration_seconds = int(generation_duration)
        exam.generation_timestamp = end_time

        await db.commit()

        logger.info(f"Exam {exam.id} generated successfully in {generation_duration}s")

        # Prepare response
        return {
            "exam_id": str(exam.id),
            "title": exam.title,
            "topic": exam.topic,
            "num_questions": exam.num_questions,
            "question_type": exam.question_type,
            "difficulty_level": exam.difficulty_level,
            "questions": [
                {
                    "question_number": q.question_number,
                    "question_text": q.question_text,
                    "question_type": q.question_type,
                    "difficulty_level": q.difficulty_level,
                    "options": q.options,
                    "correct_answer": q.correct_answer,
                    "explanation": q.explanation,
                    "key_concepts": q.key_concepts
                }
                for q in question_records
            ],
            "sources": context.get("sources", []),
            "generation_duration_seconds": generation_duration,
            "status": "completed"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating exam: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating exam: {str(e)}"
        )


@router.get("/{exam_id}")
async def get_exam(
    exam_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """Get exam details with all questions."""
    try:
        result = await db.execute(
            select(Exam).where(
                (Exam.id == UUID(exam_id)) &
                (Exam.user_id == UUID(user_id))
            )
        )
        exam = result.scalars().first()

        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exam not found"
            )

        return {
            "id": str(exam.id),
            "title": exam.title,
            "topic": exam.topic,
            "description": exam.description,
            "question_type": exam.question_type,
            "difficulty_level": exam.difficulty_level,
            "num_questions": exam.num_questions,
            "time_duration_minutes": exam.time_duration_minutes,
            "source_preference": exam.source_preference,
            "custom_instructions": exam.custom_instructions,
            "llm_provider": exam.llm_provider,
            "llm_model": exam.llm_model,
            "generation_duration_seconds": exam.generation_duration_seconds,
            "is_published": exam.is_published,
            "is_shared": exam.is_shared,
            "created_at": exam.created_at.isoformat() if exam.created_at else None,
            "questions": [
                {
                    "question_number": q.question_number,
                    "question_text": q.question_text,
                    "question_type": q.question_type,
                    "difficulty_level": q.difficulty_level,
                    "options": q.options,
                    "correct_answer": q.correct_answer,
                    "explanation": q.explanation,
                    "key_concepts": q.key_concepts
                }
                for q in exam.questions
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting exam: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving exam: {str(e)}"
        )


@router.get("/")
async def list_exams(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """List user's exams."""
    try:
        result = await db.execute(
            select(Exam).where(
                Exam.user_id == UUID(user_id)
            ).order_by(Exam.created_at.desc())
        )
        exams = result.scalars().all()

        return {
            "exams": [
                {
                    "id": str(exam.id),
                    "title": exam.title,
                    "topic": exam.topic,
                    "num_questions": exam.num_questions,
                    "question_type": exam.question_type,
                    "difficulty_level": exam.difficulty_level,
                    "is_published": exam.is_published,
                    "is_shared": exam.is_shared,
                    "created_at": exam.created_at.isoformat() if exam.created_at else None,
                    "generation_duration_seconds": exam.generation_duration_seconds
                }
                for exam in exams
            ],
            "total": len(exams)
        }
    except Exception as e:
        logger.error(f"Error listing exams: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing exams: {str(e)}"
        )


@router.delete("/{exam_id}")
async def delete_exam(
    exam_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """Delete an exam."""
    try:
        result = await db.execute(
            select(Exam).where(
                (Exam.id == UUID(exam_id)) &
                (Exam.user_id == UUID(user_id))
            )
        )
        exam = result.scalars().first()

        if not exam:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Exam not found"
            )

        await db.delete(exam)
        await db.commit()

        logger.info(f"Exam {exam_id} deleted for user {user_id}")

        return {
            "message": "Exam deleted successfully",
            "exam_id": exam_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting exam: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting exam: {str(e)}"
        )
