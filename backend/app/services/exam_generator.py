"""Exam generation service."""

import logging
import json
import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime

from app.services.rag_engine import RAGEngine
from app.services.llm_service import LLMService

logger = logging.getLogger(__name__)


class ExamGenerationService:
    """Service for generating exams using RAG and LLM."""

    def __init__(self, rag_engine: RAGEngine, llm_service: LLMService):
        """Initialize exam generation service."""
        self.rag_engine = rag_engine
        self.llm_service = llm_service

    def build_exam_prompt(
        self,
        topic: str,
        context: str,
        question_type: str,
        difficulty_level: str,
        num_questions: int,
        custom_instructions: Optional[str] = None,
        custom_prompt: Optional[str] = None
    ) -> str:
        """Build the prompt for exam generation."""
        
        if custom_prompt:
            # User provided custom prompt
            prompt = custom_prompt.format(
                context=context,
                topic=topic,
                num_questions=num_questions,
                question_type=question_type,
                difficulty_level=difficulty_level,
                custom_instructions=custom_instructions or ""
            )
        else:
            # Use default prompt template
            prompt = f"""You are an expert exam creator. Based on the provided context, create {num_questions} {question_type} questions about "{topic}".

Difficulty Level: {difficulty_level}

Context/Learning Material:
{context}

Requirements:
- Each question should test understanding of the material
- Questions should be clear and unambiguous
- Include answer key with explanations
{f"- Additional instructions: {custom_instructions}" if custom_instructions else ""}

Please generate the questions in the following JSON format:
{{
    "questions": [
        {{
            "number": 1,
            "question": "Question text here",
            "type": "{question_type}",
            "difficulty": "{difficulty_level}",
            "options": ["Option A", "Option B", "Option C", "Option D"],  // For MCQ only
            "correct_answer": "B",  // or full text for non-MCQ
            "explanation": "Explanation of the answer"
        }}
    ]
}}

Generate {num_questions} questions now:"""
        
        return prompt

    def parse_exam_response(self, response: str, num_questions: int) -> Dict[str, Any]:
        """Parse LLM response into structured exam questions."""
        try:
            # Try to extract JSON from response
            import re
            json_match = re.search(r'\{[\s\S]*\}', response)
            if json_match:
                exam_data = json.loads(json_match.group())
            else:
                # If no JSON found, return raw response
                logger.warning("No JSON found in LLM response")
                exam_data = {"questions": [], "raw_response": response}

            return exam_data

        except json.JSONDecodeError as e:
            logger.error(f"Error parsing exam JSON: {e}")
            return {
                "questions": [],
                "error": str(e),
                "raw_response": response
            }

    def validate_questions(self, questions: List[Dict[str, Any]]) -> bool:
        """Validate question structure."""
        try:
            for question in questions:
                assert "question" in question, "Missing 'question' field"
                assert "correct_answer" in question, "Missing 'correct_answer' field"
                
                if question.get("type") == "MCQ":
                    assert "options" in question, "MCQ must have 'options'"
                    assert len(question["options"]) >= 2, "MCQ must have at least 2 options"

            return True
        except AssertionError as e:
            logger.warning(f"Question validation failed: {e}")
            return False

    def generate_exam(
        self,
        topic: str,
        user_id: str,
        question_type: str = "MCQ",
        difficulty_level: str = "intermediate",
        num_questions: int = 10,
        source_preference: str = "mixed",
        custom_instructions: Optional[str] = None,
        custom_prompt: Optional[str] = None,
        document_ids: Optional[List[str]] = None,
        search_internet: bool = False
    ) -> Dict[str, Any]:
        """
        Generate an exam using RAG and LLM.

        Args:
            topic: Exam topic
            user_id: User ID
            question_type: Type of questions (MCQ, short_answer, etc.)
            difficulty_level: Difficulty level
            num_questions: Number of questions to generate
            source_preference: Source preference (user_documents, internet, mixed)
            custom_instructions: Custom exam instructions
            custom_prompt: Custom prompt template
            document_ids: List of specific document IDs to use
            search_internet: Whether to include internet search

        Returns:
            Generated exam structure
        """
        try:
            logger.info(f"Generating exam for topic: {topic}")

            # Step 1: Retrieve relevant context
            filter_conditions = {"source_type": source_preference} if source_preference != "mixed" else None
            
            # For user documents
            if source_preference in ["user_documents", "mixed"]:
                user_results = self.rag_engine.retrieve_context(
                    query=topic,
                    top_k=5,
                    user_id=user_id,
                    source_type="user_document"
                )
            else:
                user_results = []

            # For internet sources
            if source_preference in ["internet", "mixed"]:
                internet_results = self.rag_engine.retrieve_context(
                    query=topic,
                    top_k=5,
                    source_type="internet"
                )
            else:
                internet_results = []

            # Combine results
            all_results = user_results + internet_results

            if not all_results:
                logger.warning("No context found for exam generation")

            # Step 2: Combine context
            context, source_urls = self.rag_engine.combine_context(all_results)

            # Step 3: Build prompt
            prompt = self.build_exam_prompt(
                topic=topic,
                context=context or "No context available. Generate questions based on general knowledge.",
                question_type=question_type,
                difficulty_level=difficulty_level,
                num_questions=num_questions,
                custom_instructions=custom_instructions,
                custom_prompt=custom_prompt
            )

            # Step 4: Generate using LLM
            logger.info("Calling LLM to generate questions...")
            system_message = "You are an expert exam creator. Generate high-quality exam questions in JSON format."
            response = self.llm_service.generate(
                prompt=prompt,
                temperature=0.7,
                max_tokens=2048,
                system_message=system_message
            )

            # Step 5: Parse response
            exam_data = self.parse_exam_response(response, num_questions)

            # Step 6: Validate questions
            questions = exam_data.get("questions", [])
            if questions:
                is_valid = self.validate_questions(questions)
                if not is_valid:
                    logger.warning("Some questions failed validation")

            # Return structured exam
            exam_result = {
                "exam_id": str(uuid.uuid4()),
                "topic": topic,
                "question_type": question_type,
                "difficulty_level": difficulty_level,
                "num_questions_requested": num_questions,
                "num_questions_generated": len(questions),
                "questions": questions,
                "sources": self.rag_engine.extract_sources(all_results),
                "generated_at": datetime.utcnow().isoformat(),
                "status": "success" if questions else "failed"
            }

            logger.info(f"✅ Exam generated with {len(questions)} questions")
            return exam_result

        except Exception as e:
            logger.error(f"❌ Error generating exam: {e}")
            return {
                "exam_id": str(uuid.uuid4()),
                "topic": topic,
                "status": "failed",
                "error": str(e),
                "generated_at": datetime.utcnow().isoformat()
            }
