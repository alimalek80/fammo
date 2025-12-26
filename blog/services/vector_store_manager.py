"""
OpenAI Vector Store Manager for Blog Index.
Manages uploading blog index to OpenAI and maintaining vector store.
"""
import logging
from pathlib import Path
from django.conf import settings
from django.core.cache import cache
from openai import OpenAI

logger = logging.getLogger(__name__)

# Cache key for vector store ID
VECTOR_STORE_CACHE_KEY = 'blog_index_vector_store_id'


def get_openai_client():
    """Returns OpenAI client."""
    return OpenAI(api_key=settings.OPENAI_API_KEY)


def upload_blog_index_to_openai():
    """
    Uploads the blog index JSON file to OpenAI and creates/updates vector store.
    
    Returns:
        str: Vector store ID
    """
    client = get_openai_client()
    
    # Path to blog index file
    blog_index_file = Path(settings.MEDIA_ROOT) / 'blog_index' / 'published_blogs.json'
    
    if not blog_index_file.exists():
        raise FileNotFoundError(f"Blog index file not found at {blog_index_file}")
    
    logger.info("Uploading blog index to OpenAI...")
    
    # Upload file to OpenAI
    with open(blog_index_file, 'rb') as f:
        file_response = client.files.create(
            file=f,
            purpose='assistants'
        )
    
    file_id = file_response.id
    logger.info(f"Uploaded blog index file: {file_id}")
    
    # Check if we have an existing vector store
    vector_store_id = cache.get(VECTOR_STORE_CACHE_KEY)
    
    if vector_store_id:
        try:
            # Update existing vector store by adding new file
            logger.info(f"Updating existing vector store: {vector_store_id}")
            client.vector_stores.files.create(
                vector_store_id=vector_store_id,
                file_id=file_id
            )
            logger.info(f"Updated vector store: {vector_store_id}")
            return vector_store_id
        except Exception as e:
            logger.warning(f"Failed to update vector store {vector_store_id}: {e}")
            logger.info("Creating new vector store...")
            vector_store_id = None
    
    # Create new vector store
    if not vector_store_id:
        vector_store = client.vector_stores.create(
            name="FAMMO Blog Index",
            file_ids=[file_id]
        )
        vector_store_id = vector_store.id
        
        # Cache the vector store ID (cache for 30 days)
        cache.set(VECTOR_STORE_CACHE_KEY, vector_store_id, timeout=60*60*24*30)
        logger.info(f"Created new vector store: {vector_store_id}")
    
    return vector_store_id


def get_vector_store_id():
    """
    Gets the cached vector store ID. If not exists, uploads and creates one.
    
    Returns:
        str: Vector store ID
    """
    vector_store_id = cache.get(VECTOR_STORE_CACHE_KEY)
    
    if not vector_store_id:
        logger.info("Vector store ID not cached, uploading blog index...")
        vector_store_id = upload_blog_index_to_openai()
    
    return vector_store_id


def force_refresh_vector_store():
    """
    Forces a refresh of the vector store by uploading the latest blog index.
    Call this after publishing new blog posts.
    
    Returns:
        str: Vector store ID
    """
    logger.info("Force refreshing vector store...")
    return upload_blog_index_to_openai()
