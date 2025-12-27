"""
AI Blog Generation Service using OpenAI Responses API.

This service:
1. Picks a TODO topic
2. Generates SEO-friendly blog content with link suggestions and image prompts
3. Creates social media drafts (LinkedIn, X/Twitter)
4. Creates unpublished BlogPost draft for admin review
5. Marks topic as COMPLETED on success or reverts on failure
"""
import json
import logging
from django.conf import settings
from django.utils import timezone
from django.utils.text import slugify
from openai import OpenAI

from blog.models import BlogTopic, BlogGenerationRequest, BlogPost, BlogPostImageSuggestion
from .topic_selector import pick_next_topic, mark_topic_completed, revert_topic_to_todo
from .blog_index_generator import generate_blog_index
from .vector_store_manager import get_vector_store_id

logger = logging.getLogger(__name__)


# OpenAI client wrapper for mockability
def get_openai_client():
    """Returns OpenAI client. Can be mocked in tests."""
    return OpenAI(api_key=settings.OPENAI_API_KEY)



def build_generation_prompt(topic, tone='professional'):
    """
    Builds the prompt for OpenAI API with detailed instructions.
    
    Args:
        topic: BlogTopic instance
        tone: Tone of the blog post
    
    Returns:
        String containing the complete prompt
    """
    # Provide guidance to AI - if admin provides keywords, respect them; otherwise generate optimal ones
    keyword_guidance = ""
    if topic.primary_keyword:
        keyword_guidance = f"Primary keyword (use this): {topic.primary_keyword}"
    else:
        keyword_guidance = "Research and select the most effective primary keyword for SEO"
    
    if topic.secondary_keywords:
        keyword_guidance += f"\nSecondary keywords (incorporate these): {topic.secondary_keywords}"
    else:
        keyword_guidance += "\nGenerate 3-5 relevant secondary keywords for optimal SEO"
    
    target_audience = topic.target_audience or "General audience interested in pet care and veterinary services"
    notes = topic.notes or ""
    
    prompt = f"""You are an expert SEO content writer for FAMMO (https://fammo.ai), a platform revolutionizing pet healthcare with AI-driven solutions connecting pet owners with veterinary services.

TASK: Write a comprehensive, SEO-optimized blog post about "{topic.title}" in {topic.language}.

IMPORTANT: You have access to a file_search tool containing our published blog posts. Use it to find REAL blog posts related to the topic you're writing about.

REQUIREMENTS:

1. BLOG POST CONTENT:
   - Title: Compelling, SEO-friendly (50-60 chars) - refine the provided title if needed
   - Slug: URL-friendly (lowercase, hyphens)
   - Meta description: Engaging, under 160 characters, with call-to-action
   - Keywords: {keyword_guidance}
   - Target audience: {target_audience}
   - Content length: 1200-1800 words
   - Tone: {tone}
   - Format: Markdown with proper headings (##, ###), bullet points, and bold/italic emphasis
   - Structure: Introduction → Main sections with subheadings → Conclusion with CTA
   
2. INTERNAL LINK BOXES (CRITICAL - USE file_search TOOL):
   - FIRST: Use the file_search tool to find published blogs related to this topic
   - Look for blogs in the same language: {topic.language}
   - Search for related topics, similar keywords, or complementary content
   - CREATE EXACTLY 2 visually distinct call-out boxes using REAL blogs found via file_search:
   
> **📖 Related Read: [REAL Blog Title](https://fammo.ai/blog/REAL-SLUG)**
>
> Brief compelling description (1-2 sentences) explaining why readers should check this post and how it relates to the current section.

   - Place these boxes strategically after relevant paragraphs
   - Use ONLY real slugs and titles returned from file_search
   - Write engaging, benefit-focused descriptions that entice clicks
   - If file_search returns fewer than 2 posts, create boxes for what's available
   - Also return these links in the internal_links array with placement_hint
   
3. EXTERNAL LINKS (EMBED IN TEXT):
   - EMBED 3-5 reputable external sources directly in the markdown content
   - Use format: [anchor text](https://actual-url.com)
   - Prioritize: AVMA, AKC, PetMD, veterinary journals, .edu, .gov sites
   - Place links naturally where they provide citations or additional value
   - Return the same links in external_links array with placement_hint for reference

4. IMAGE PROMPTS (EMBED IN MARKDOWN):
   - EMBED 2-3 image placeholders throughout the content using this format:
   
📷 **[Image: Alt text here]**
*AI Prompt: Detailed image generation prompt here*
   
   - Place image prompts at natural breaks between paragraphs or sections
   - Make prompts detailed and professional for AI image generators
   - Also return thumbnail and inline image data in the images object

5. EXAMPLE WITH INTERNAL LINK BOX:

## Understanding Pet Nutrition

Proper nutrition is essential for your pet's health and longevity. Different pets require different nutritional approaches based on their species, age, and health conditions.

> **📖 Related Read: [Understanding Pet Allergies](https://fammo.ai/blog/understanding-pet-allergies)**
>
> Discover how food choices affect pet allergies and how tailored diets can reduce symptoms and improve wellbeing.

📷 **[Image: Happy dog eating from a stainless steel bowl]**
*AI Prompt: Professional photograph of a healthy golden retriever eating nutritious kibble from a clean stainless steel bowl in a modern kitchen, natural lighting, high quality*

Research from the [American Veterinary Medical Association](https://avma.org) shows that...

6. SOCIAL MEDIA DRAFTS:
   
   A) LINKEDIN POST (600-1200 characters):
      - Hook: Compelling opening question or statement
      - Key takeaway from the blog
      - Call-to-action: Encourage reading the full blog post
      - 3-7 hashtags (mix popular + niche)
      - FAMMO brand voice: Professional, caring, innovative
      - Include: "Read more at https://fammo.ai/blog/[slug]"
   
   B) X/TWITTER POST (≤280 characters):
      - Punchy, attention-grabbing
      - 1-2 key insights
      - 3-6 relevant hashtags
      - Link: https://fammo.ai/blog/[slug]
      - Urgent/intriguing tone

ADDITIONAL NOTES: {notes}

RESPONSE FORMAT (STRICT JSON):
{{
  "blog": {{
    "title": "...",
    "slug": "...",
    "meta_description": "...",
    "keywords": ["...", "..."],
    "markdown": "# Introduction\\n\\n...\\n\\n> **📖 Related Read: [Real Title](https://fammo.ai/blog/real-slug)**\\n>\\n> Compelling description...\\n\\n📷 **[Image: Alt]**\\n*AI Prompt: ...*\\n\\n..."
  }},
  "internal_links": [
    {{"anchor": "Real blog title from file_search", "target_slug": "real-slug-from-file-search", "placement_hint": "After section about..."}}
  ],
  "external_links": [
    {{"anchor": "...", "url": "...", "placement_hint": "..."}}
  ],
  "images": {{
    "thumbnail": {{"alt": "...", "prompt": "..."}},
    "inline": [
      {{"alt": "...", "prompt": "...", "placement_hint": "..."}},
      {{"alt": "...", "prompt": "...", "placement_hint": "..."}}
    ]
  }},
  "social": {{
    "linkedin": {{
      "text": "...",
      "hook": "...",
      "hashtags": ["PetCare", "VetTech", "FAMMO", "..."]
    }},
    "x": {{
      "text": "...",
      "hashtags": ["PetHealth", "AI", "VetCare", "..."]
    }}
  }}
}}

CRITICAL: 
- USE file_search tool to find real published blogs
- Create EXACTLY 2 internal link boxes using ONLY real blogs from file_search
- Use the > blockquote format with 📖 emoji for link boxes
- Write compelling descriptions that highlight the value to the reader
- Place boxes after complete paragraphs, not mid-paragraph
- Embed external links naturally in text
- Use 📷 emoji for image prompts
- Return ONLY valid JSON, no markdown code blocks or explanations
"""
    return prompt


def validate_ai_response(response_data):
    """
    Validates the structure of AI response JSON.
    
    Args:
        response_data: Parsed JSON dict
    
    Returns:
        Tuple (is_valid: bool, error_message: str or None)
    """
    required_keys = ['blog', 'internal_links', 'external_links', 'images', 'social']
    
    for key in required_keys:
        if key not in response_data:
            return False, f"Missing required key: {key}"
    
    # Validate blog structure
    blog = response_data.get('blog', {})
    blog_required = ['title', 'slug', 'meta_description', 'keywords', 'markdown']
    for key in blog_required:
        if key not in blog:
            return False, f"Missing required blog key: {key}"
    
    # Validate social structure
    social = response_data.get('social', {})
    if 'linkedin' not in social or 'x' not in social:
        return False, "Missing social media drafts"
    
    return True, None


def format_social_drafts(response_data):
    """
    Formats social media drafts as plain text for admin to copy/paste.
    
    Args:
        response_data: Parsed JSON dict
    
    Returns:
        Tuple (linkedin_draft: str, x_draft: str)
    """
    social = response_data.get('social', {})
    
    # LinkedIn draft
    linkedin = social.get('linkedin', {})
    linkedin_text = linkedin.get('text', '')
    linkedin_hashtags = ' '.join([f"#{tag}" for tag in linkedin.get('hashtags', [])])
    linkedin_draft = f"{linkedin_text}\n\n{linkedin_hashtags}".strip()
    
    # X/Twitter draft
    x = social.get('x', {})
    x_text = x.get('text', '')
    x_hashtags = ' '.join([f"#{tag}" for tag in x.get('hashtags', [])])
    x_draft = f"{x_text} {x_hashtags}".strip()
    
    return linkedin_draft, x_draft


def generate_for_next_topic(language, tone='professional', created_by=None):
    """
    Main function to generate blog content for the next available topic.
    
    This function:
    1. Picks next TODO topic for the language
    2. Creates a BlogGenerationRequest
    3. Calls OpenAI API with structured prompt
    4. Validates response
    5. Creates unpublished BlogPost draft
    6. Creates ImageSuggestion records
    7. Stores social media drafts
    8. Marks topic as COMPLETED on success
    
    Args:
        language: Language code ('en', 'tr', 'fi')
        tone: Tone of the blog post
        created_by: User instance who initiated the request
    
    Returns:
        BlogGenerationRequest instance
    
    Raises:
        ValueError: If no TODO topics available for the language
    """
    # Step 1: Pick next topic (locks row, changes status to IN_PROGRESS)
    topic = pick_next_topic(language)
    
    if not topic:
        raise ValueError(f"No TODO topics available for language: {language}")
    
    # Step 2: Create request record
    request = BlogGenerationRequest.objects.create(
        topic=topic,
        language=language,
        tone=tone,
        status='PENDING',
        created_by=created_by
    )
    
    try:
        # Step 3: Update blog index before generation (ensures fresh data)
        logger.info("Updating blog index JSON before generation...")
        generate_blog_index()
        
        # Step 4: Get or create vector store for file_search
        vector_store_id = get_vector_store_id()
        logger.info(f"Using vector store ID: {vector_store_id}")
        
        # Step 5: Build prompt
        prompt = build_generation_prompt(topic, tone)
        
        # Step 6: Call OpenAI Responses API with file_search tool
        logger.info(f"Calling OpenAI Responses API for topic: {topic.title}")
        client = get_openai_client()
        
        response = client.responses.create(
            model="gpt-4o",
            input=prompt,
            instructions="You are an expert SEO content writer for FAMMO. You always respond with valid JSON only.",
            tools=[{
                "type": "file_search",
                "vector_store_ids": [vector_store_id]
            }],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "blog_generation_response",
                    "schema": {
                            "type": "object",
                            "properties": {
                                "blog": {
                                    "type": "object",
                                    "properties": {
                                        "title": {"type": "string"},
                                        "slug": {"type": "string"},
                                        "meta_description": {"type": "string"},
                                        "keywords": {"type": "array", "items": {"type": "string"}},
                                        "markdown": {"type": "string"}
                                    },
                                    "required": ["title", "slug", "meta_description", "keywords", "markdown"],
                                    "additionalProperties": False
                                },
                                "internal_links": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "anchor": {"type": "string"},
                                            "target_slug": {"type": "string"},
                                            "placement_hint": {"type": "string"}
                                        },
                                        "required": ["anchor", "target_slug", "placement_hint"],
                                        "additionalProperties": False
                                    }
                                },
                                "external_links": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "anchor": {"type": "string"},
                                            "url": {"type": "string"},
                                            "placement_hint": {"type": "string"}
                                        },
                                        "required": ["anchor", "url", "placement_hint"],
                                        "additionalProperties": False
                                    }
                                },
                                "images": {
                                    "type": "object",
                                    "properties": {
                                        "thumbnail": {
                                            "type": "object",
                                            "properties": {
                                                "alt": {"type": "string"},
                                                "prompt": {"type": "string"}
                                            },
                                            "required": ["alt", "prompt"],
                                            "additionalProperties": False
                                        },
                                        "inline": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "alt": {"type": "string"},
                                                    "prompt": {"type": "string"},
                                                    "placement_hint": {"type": "string"}
                                                },
                                                "required": ["alt", "prompt", "placement_hint"],
                                                "additionalProperties": False
                                            }
                                        }
                                    },
                                    "required": ["thumbnail", "inline"],
                                    "additionalProperties": False
                                },
                                "social": {
                                    "type": "object",
                                    "properties": {
                                        "linkedin": {
                                            "type": "object",
                                            "properties": {
                                                "text": {"type": "string"},
                                                "hook": {"type": "string"},
                                                "hashtags": {"type": "array", "items": {"type": "string"}}
                                            },
                                            "required": ["text", "hook", "hashtags"],
                                            "additionalProperties": False
                                        },
                                        "x": {
                                            "type": "object",
                                            "properties": {
                                                "text": {"type": "string"},
                                                "hashtags": {"type": "array", "items": {"type": "string"}}
                                            },
                                            "required": ["text", "hashtags"],
                                            "additionalProperties": False
                                        }
                                    },
                                    "required": ["linkedin", "x"],
                                    "additionalProperties": False
                                }
                            },
                            "required": ["blog", "internal_links", "external_links", "images", "social"],
                            "additionalProperties": False
                        }
                }
            },
            temperature=0.7,
            max_output_tokens=4000
        )
        
        # Step 6: Parse and validate response
        # Extract text from the response output
        response_text = None
        if response.output and len(response.output) > 0:
            for item in response.output:
                if item.type == "message" and item.role == "assistant":
                    for content_item in item.content:
                        if content_item.type == "output_text":
                            response_text = content_item.text
                            break
                    if response_text:
                        break
        
        if not response_text:
            raise ValueError("No text output received from OpenAI Responses API")
        
        logger.info(f"Received response from OpenAI (length: {len(response_text)})")
        
        try:
            response_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from OpenAI: {e}")
        
        is_valid, error_msg = validate_ai_response(response_data)
        if not is_valid:
            raise ValueError(f"Invalid response structure: {error_msg}")
        
        # Step 7: Create BlogPost draft
        blog_data = response_data['blog']
        
        # Ensure slug is unique
        base_slug = slugify(blog_data['slug'])
        slug = base_slug
        counter = 1
        while BlogPost.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        blog_post = BlogPost.objects.create(
            title=blog_data['title'],
            slug=slug,
            content=blog_data['markdown'],
            meta_description=blog_data['meta_description'][:255],
            meta_keywords=', '.join(blog_data.get('keywords', []))[:255],
            language=language,
            is_published=False,  # Draft - requires admin approval
            author=created_by
        )
        
        logger.info(f"Created draft BlogPost: {blog_post.slug}")
        
        # Step 8: Create image suggestions
        images_data = response_data.get('images', {})
        
        # Thumbnail
        thumbnail = images_data.get('thumbnail', {})
        if thumbnail:
            prompt = thumbnail.get('prompt', '')
            prompt_with_aspect = f"{prompt} (Aspect ratio: 16:9)" if prompt else "Aspect ratio: 16:9"
            BlogPostImageSuggestion.objects.create(
                post=blog_post,
                image_type='THUMBNAIL',
                alt_text=thumbnail.get('alt', '')[:200],
                prompt=prompt_with_aspect,
                placement_hint='Featured image'
            )
        
        # Inline images
        for inline_img in images_data.get('inline', []):
            prompt = inline_img.get('prompt', '')
            prompt_with_aspect = f"{prompt} (Aspect ratio: 16:9)" if prompt else "Aspect ratio: 16:9"
            BlogPostImageSuggestion.objects.create(
                post=blog_post,
                image_type='INLINE',
                alt_text=inline_img.get('alt', '')[:200],
                prompt=prompt_with_aspect,
                placement_hint=inline_img.get('placement_hint', '')[:200]
            )
        
        # Step 9: Format and store social drafts
        linkedin_draft, x_draft = format_social_drafts(response_data)
        
        # Step 10: Update request record
        request.blog_post = blog_post
        request.generated_json = response_data
        request.linkedin_draft = linkedin_draft
        request.x_draft = x_draft
        request.status = 'GENERATED'
        request.save()
        
        # Step 11: Mark topic as COMPLETED
        mark_topic_completed(topic)
        
        logger.info(f"Successfully generated blog for topic: {topic.title}")
        return request
        
    except Exception as e:
        # Handle failures gracefully
        logger.error(f"Blog generation failed for topic {topic.title}: {e}")
        
        request.status = 'FAILED'
        request.error_message = str(e)
        request.save()
        
        # Revert topic to TODO so it can be retried
        revert_topic_to_todo(topic)
        
        raise


def generate_blog_from_topic(topic, language, tone, created_by):
    """
    Generate a blog from a specific topic (instead of picking next one).
    
    Args:
        topic: BlogTopic instance to generate from
        language: Language code (e.g., 'en', 'tr')
        tone: Tone of the blog post
        created_by: User who initiated the generation
    
    Returns:
        BlogGenerationRequest instance
    
    Raises:
        ValueError: If topic is not TODO status
        Exception: For any other errors during generation
    """
    from blog.services.topic_selector import mark_topic_in_progress
    
    # Validate topic status
    if topic.status != 'TODO':
        raise ValueError(f"Topic '{topic.title}' is not available (status: {topic.status})")
    
    # Mark topic as IN_PROGRESS
    mark_topic_in_progress(topic)
    
    # Create generation request
    request = BlogGenerationRequest.objects.create(
        topic=topic,
        language=language,
        tone=tone,
        created_by=created_by,
        status='PENDING'
    )
    
    try:
        # Step 1: Refresh blog index
        logger.info("Updating blog index JSON before generation...")
        generate_blog_index()
        
        # Step 2: Get vector store ID
        vector_store_id = get_vector_store_id()
        logger.info(f"Using vector store ID: {vector_store_id}")
        
        # Step 3: Build prompt
        prompt = build_generation_prompt(topic, tone)
        
        # Step 4: Call OpenAI Responses API with file_search tool
        logger.info(f"Calling OpenAI Responses API for topic: {topic.title}")
        client = get_openai_client()
        
        response = client.responses.create(
            model="gpt-4o",
            input=prompt,
            instructions="You are an expert SEO content writer for FAMMO. You always respond with valid JSON only.",
            tools=[{
                "type": "file_search",
                "vector_store_ids": [vector_store_id]
            }],
            text={
                "format": {
                    "type": "json_schema",
                    "name": "blog_generation_response",
                    "schema": {
                            "type": "object",
                            "properties": {
                                "blog": {
                                    "type": "object",
                                    "properties": {
                                        "title": {"type": "string"},
                                        "slug": {"type": "string"},
                                        "meta_description": {"type": "string"},
                                        "keywords": {"type": "array", "items": {"type": "string"}},
                                        "markdown": {"type": "string"}
                                    },
                                    "required": ["title", "slug", "meta_description", "keywords", "markdown"],
                                    "additionalProperties": False
                                },
                                "internal_links": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "anchor": {"type": "string"},
                                            "target_slug": {"type": "string"},
                                            "placement_hint": {"type": "string"}
                                        },
                                        "required": ["anchor", "target_slug", "placement_hint"],
                                        "additionalProperties": False
                                    }
                                },
                                "external_links": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "anchor": {"type": "string"},
                                            "url": {"type": "string"},
                                            "placement_hint": {"type": "string"}
                                        },
                                        "required": ["anchor", "url", "placement_hint"],
                                        "additionalProperties": False
                                    }
                                },
                                "images": {
                                    "type": "object",
                                    "properties": {
                                        "thumbnail": {
                                            "type": "object",
                                            "properties": {
                                                "alt": {"type": "string"},
                                                "prompt": {"type": "string"}
                                            },
                                            "required": ["alt", "prompt"],
                                            "additionalProperties": False
                                        },
                                        "inline": {
                                            "type": "array",
                                            "items": {
                                                "type": "object",
                                                "properties": {
                                                    "alt": {"type": "string"},
                                                    "prompt": {"type": "string"},
                                                    "placement_hint": {"type": "string"}
                                                },
                                                "required": ["alt", "prompt", "placement_hint"],
                                                "additionalProperties": False
                                            }
                                        }
                                    },
                                    "required": ["thumbnail", "inline"],
                                    "additionalProperties": False
                                },
                                "social": {
                                    "type": "object",
                                    "properties": {
                                        "linkedin": {
                                            "type": "object",
                                            "properties": {
                                                "text": {"type": "string"},
                                                "hook": {"type": "string"},
                                                "hashtags": {"type": "array", "items": {"type": "string"}}
                                            },
                                            "required": ["text", "hook", "hashtags"],
                                            "additionalProperties": False
                                        },
                                        "x": {
                                            "type": "object",
                                            "properties": {
                                                "text": {"type": "string"},
                                                "hashtags": {"type": "array", "items": {"type": "string"}}
                                            },
                                            "required": ["text", "hashtags"],
                                            "additionalProperties": False
                                        }
                                    },
                                    "required": ["linkedin", "x"],
                                    "additionalProperties": False
                                }
                            },
                            "required": ["blog", "internal_links", "external_links", "images", "social"],
                            "additionalProperties": False
                        }
                }
            },
            temperature=0.7,
            max_output_tokens=4000
        )
        
        # Step 5: Parse and validate response
        # Extract text from the response output
        response_text = None
        if response.output and len(response.output) > 0:
            for item in response.output:
                if item.type == "message" and item.role == "assistant":
                    for content_item in item.content:
                        if content_item.type == "output_text":
                            response_text = content_item.text
                            break
                    if response_text:
                        break
        
        if not response_text:
            raise ValueError("No text output received from OpenAI Responses API")
        
        logger.info(f"Received response from OpenAI (length: {len(response_text)})")
        
        try:
            response_data = json.loads(response_text)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON response from OpenAI: {e}")
        
        is_valid, error_msg = validate_ai_response(response_data)
        if not is_valid:
            raise ValueError(f"Invalid response structure: {error_msg}")
        
        # Step 6: Create BlogPost draft
        blog_data = response_data['blog']
        
        # Ensure slug is unique
        base_slug = slugify(blog_data['slug'])
        slug = base_slug
        counter = 1
        while BlogPost.objects.filter(slug=slug).exists():
            slug = f"{base_slug}-{counter}"
            counter += 1
        
        blog_post = BlogPost.objects.create(
            title=blog_data['title'],
            slug=slug,
            content=blog_data['markdown'],
            meta_description=blog_data['meta_description'][:255],
            meta_keywords=', '.join(blog_data.get('keywords', []))[:255],
            language=language,
            is_published=False,  # Draft - requires admin approval
            author=created_by
        )
        
        logger.info(f"Created draft BlogPost: {blog_post.slug}")
        
        # Step 7: Create image suggestions
        images_data = response_data.get('images', {})
        
        # Thumbnail
        thumbnail = images_data.get('thumbnail', {})
        if thumbnail:
            prompt = thumbnail.get('prompt', '')
            prompt_with_aspect = f"{prompt} (Aspect ratio: 16:9)" if prompt else "Aspect ratio: 16:9"
            BlogPostImageSuggestion.objects.create(
                post=blog_post,
                image_type='THUMBNAIL',
                alt_text=thumbnail.get('alt', '')[:200],
                prompt=prompt_with_aspect,
                placement_hint='Featured image'
            )
        
        # Inline images
        for inline_img in images_data.get('inline', []):
            prompt = inline_img.get('prompt', '')
            prompt_with_aspect = f"{prompt} (Aspect ratio: 16:9)" if prompt else "Aspect ratio: 16:9"
            BlogPostImageSuggestion.objects.create(
                post=blog_post,
                image_type='INLINE',
                alt_text=inline_img.get('alt', '')[:200],
                prompt=prompt_with_aspect,
                placement_hint=inline_img.get('placement_hint', '')[:200]
            )
        
        logger.info(f"Created {images_data.get('inline', []).__len__() + 1} image suggestions")
        
        # Step 8: Format and store social drafts
        linkedin_draft, x_draft = format_social_drafts(response_data)
        
        # Step 9: Update generation request
        request.blog_post = blog_post
        request.generated_json = response_data
        request.linkedin_draft = linkedin_draft
        request.x_draft = x_draft
        request.status = 'GENERATED'
        request.save()
        
        # Step 10: Mark topic as COMPLETED
        mark_topic_completed(topic)
        
        logger.info(f"Successfully generated blog from specific topic: {topic.title}")
        return request
        
    except Exception as e:
        logger.error(f"Blog generation failed for topic {topic.title}: {e}")
        
        request.status = 'FAILED'
        request.error_message = str(e)
        request.save()
        
        # Revert topic to TODO
        revert_topic_to_todo(topic)
        
        raise
