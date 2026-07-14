"""Document API endpoints."""

import os
import logging
from io import BytesIO
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import Document, DocumentChunk, User
from app.utils.security import get_current_user_id
from app.services.document_processor import DocumentProcessor, TextChunker
from app.services.embeddings import get_embeddings_service
from app.services.qdrant_service import get_qdrant_service
from app.config import settings

logger = logging.getLogger(__name__)
router = APIRouter()

# Allowed file types
ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx", ".xlsx"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """Upload and process a document."""
    try:
        # Validate file
        file_ext = os.path.splitext(file.filename)[1].lower()
        if file_ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"File type {file_ext} not supported. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )

        # Read file content
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File size exceeds {MAX_FILE_SIZE / 1024 / 1024}MB limit"
            )

        # Create document record
        document = Document(
            user_id=UUID(user_id),
            file_name=file.filename,
            file_type=file_ext.lstrip("."),
            file_size_bytes=len(content),
            title=os.path.splitext(file.filename)[0],
            processing_status="processing",
            embedding_status="processing"
        )
        db.add(document)
        await db.flush()  # Get the document ID
        await db.commit()

        logger.info(f"Document created: {document.id} for user {user_id}")

        # Extract text based on file type
        text = processor.extract_text(BytesIO(content), file_ext)
        if not text or not text.strip():
            document.processing_status = "error"
            document.error_message = "No text extracted from document"
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not extract text from document"
            )

        # Clean text
        cleaned_text = processor.clean_text(text)

        # Chunk text
        chunker = TextChunker(
            chunk_size=settings.CHUNK_SIZE,
            overlap=settings.CHUNK_OVERLAP
        )
        chunks = chunker.chunk_text(cleaned_text)

        if not chunks:
            document.processing_status = "error"
            document.error_message = "Could not create chunks from text"
            await db.commit()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not create chunks from document"
            )

        logger.info(f"Created {len(chunks)} chunks from document {document.id}")

        # Generate embeddings
        embeddings_service = get_embeddings_service()
        embeddings = embeddings_service.embed_texts([chunk['text'] for chunk in chunks])

        logger.info(f"Generated {len(embeddings)} embeddings for document {document.id}")

        # Upsert to Qdrant
        qdrant = get_qdrant_service()
        collection_name = f"documents_user_{user_id}"
        
        # Create collection if not exists
        try:
            qdrant.create_collection(
                collection_name=collection_name,
                vectors_size=embeddings[0].shape[0] if len(embeddings) > 0 else 384
            )
        except Exception as e:
            logger.warning(f"Collection might already exist: {e}")

        # Upsert vectors
        points_data = []
        chunk_records = []

        for idx, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            chunk_uuid = UUID(int=hash(f"{document.id}{idx}") % (2**32 - 1))
            
            points_data.append({
                "id": chunk_uuid,
                "vector": embedding.tolist(),
                "payload": {
                    "document_id": str(document.id),
                    "user_id": user_id,
                    "chunk_index": idx,
                    "text_preview": chunk['text'][:100],
                    "source_type": "document"
                }
            })

            chunk_records.append(DocumentChunk(
                document_id=document.id,
                chunk_index=idx,
                chunk_text=chunk['text'],
                qdrant_vector_id=chunk_uuid,
                tokens_count=chunk.get('tokens', 0),
                embedding_model="all-MiniLM-L6-v2"
            ))

        qdrant.upsert_vectors(collection_name, points_data)
        db.add_all(chunk_records)

        # Update document status
        document.processing_status = "completed"
        document.embedding_status = "completed"
        document.total_chunks = len(chunks)
        document.processed_at = datetime.utcnow()
        await db.commit()

        logger.info(f"Document {document.id} processing completed successfully")

        return {
            "document_id": str(document.id),
            "file_name": document.file_name,
            "processing_status": document.processing_status,
            "total_chunks": document.total_chunks,
            "file_size_bytes": document.file_size_bytes,
            "message": "Document uploaded and processed successfully"
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error uploading document: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing document: {str(e)}"
        )


@router.get("/list")
async def list_documents(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """List user's documents."""
    try:
        result = await db.execute(
            select(Document).where(
                Document.user_id == UUID(user_id)
            ).order_by(Document.created_at.desc())
        )
        documents = result.scalars().all()

        return {
            "documents": [
                {
                    "id": str(doc.id),
                    "file_name": doc.file_name,
                    "title": doc.title,
                    "file_type": doc.file_type,
                    "file_size_bytes": doc.file_size_bytes,
                    "processing_status": doc.processing_status,
                    "total_chunks": doc.total_chunks,
                    "upload_date": doc.upload_date.isoformat() if doc.upload_date else None,
                    "processed_at": doc.processed_at.isoformat() if doc.processed_at else None
                }
                for doc in documents
            ],
            "total": len(documents)
        }
    except Exception as e:
        logger.error(f"Error listing documents: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error listing documents: {str(e)}"
        )


@router.get("/{document_id}")
async def get_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """Get document details."""
    try:
        result = await db.execute(
            select(Document).where(
                (Document.id == UUID(document_id)) &
                (Document.user_id == UUID(user_id))
            )
        )
        document = result.scalars().first()

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        return {
            "id": str(document.id),
            "file_name": document.file_name,
            "title": document.title,
            "description": document.description,
            "file_type": document.file_type,
            "file_size_bytes": document.file_size_bytes,
            "processing_status": document.processing_status,
            "total_chunks": document.total_chunks,
            "upload_date": document.upload_date.isoformat() if document.upload_date else None,
            "processed_at": document.processed_at.isoformat() if document.processed_at else None,
            "error_message": document.error_message
        }
    except Exception as e:
        logger.error(f"Error getting document: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error getting document: {str(e)}"
        )


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id)
):
    """Delete a document."""
    try:
        result = await db.execute(
            select(Document).where(
                (Document.id == UUID(document_id)) &
                (Document.user_id == UUID(user_id))
            )
        )
        document = result.scalars().first()

        if not document:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Document not found"
            )

        # Delete from Qdrant
        qdrant = get_qdrant_service()
        collection_name = f"documents_user_{user_id}"
        try:
            qdrant.delete_points(collection_name, [str(chunk.qdrant_vector_id) for chunk in document.chunks])
        except Exception as e:
            logger.warning(f"Error deleting from Qdrant: {e}")

        # Delete from database
        await db.delete(document)
        await db.commit()

        logger.info(f"Document {document_id} deleted for user {user_id}")

        return {
            "message": "Document deleted successfully",
            "document_id": document_id
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting document: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting document: {str(e)}"
        )
