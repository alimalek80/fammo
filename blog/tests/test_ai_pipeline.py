"""
Test suite for AI Blog Pipeline.

Tests cover:
1. Topic selection with race condition handling
2. Successful blog generation flow
3. Failure handling and topic status reversion
4. Social media draft formatting
5. Internal link candidate selection
"""
import json
from unittest.mock import Mock, patch
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from blog.models import (
    BlogTopic, BlogGenerationRequest, BlogPost, BlogPostImageSuggestion
)
from blog.services.topic_selector import (
    pick_next_topic, mark_topic_completed, revert_topic_to_todo
)
from blog.services.ai_blog_generator import (
    generate_for_next_topic, get_internal_link_candidates,
    validate_ai_response, format_social_drafts
)

User = get_user_model()


class TopicSelectorTests(TestCase):
    """Tests for topic selection logic."""
    
    def setUp(self):
        """Create test topics."""
        self.topic1 = BlogTopic.objects.create(
            title="Understanding Pet Nutrition",
            language="en",
            primary_keyword="pet nutrition",
            status="TODO",
            priority=5
        )
        self.topic2 = BlogTopic.objects.create(
            title="Common Dog Diseases",
            language="en",
            primary_keyword="dog diseases",
            status="TODO",
            priority=10  # Higher priority
        )
        self.topic3 = BlogTopic.objects.create(
            title="Kedi Bakımı İpuçları",
            language="tr",
            primary_keyword="kedi bakımı",
            status="TODO",
            priority=5
        )
    
    def test_pick_next_topic_selects_highest_priority(self):
        """Should select topic with highest priority."""
        topic = pick_next_topic('en')
        
        self.assertIsNotNone(topic)
        self.assertEqual(topic.id, self.topic2.id)  # Higher priority
        self.assertEqual(topic.status, 'IN_PROGRESS')
        self.assertIsNotNone(topic.last_used_at)
    
    def test_pick_next_topic_respects_language(self):
        """Should only select topics in requested language."""
        topic = pick_next_topic('tr')
        
        self.assertIsNotNone(topic)
        self.assertEqual(topic.id, self.topic3.id)
        self.assertEqual(topic.language, 'tr')
    
    def test_pick_next_topic_returns_none_when_no_todos(self):
        """Should return None when no TODO topics available."""
        # Mark all EN topics as completed
        BlogTopic.objects.filter(language='en').update(status='COMPLETED')
        
        topic = pick_next_topic('en')
        
        self.assertIsNone(topic)
    
    def test_pick_next_topic_skips_in_progress_topics(self):
        """Should skip topics that are already IN_PROGRESS."""
        self.topic2.status = 'IN_PROGRESS'
        self.topic2.save()
        
        topic = pick_next_topic('en')
        
        self.assertEqual(topic.id, self.topic1.id)  # Should pick the other TODO topic
    
    def test_mark_topic_completed(self):
        """Should mark topic as COMPLETED."""
        mark_topic_completed(self.topic1)
        
        self.topic1.refresh_from_db()
        self.assertEqual(self.topic1.status, 'COMPLETED')
    
    def test_revert_topic_to_todo(self):
        """Should revert topic to TODO and clear last_used_at."""
        self.topic1.status = 'IN_PROGRESS'
        self.topic1.last_used_at = timezone.now()
        self.topic1.save()
        
        revert_topic_to_todo(self.topic1)
        
        self.topic1.refresh_from_db()
        self.assertEqual(self.topic1.status, 'TODO')
        self.assertIsNone(self.topic1.last_used_at)


class BlogGenerationTests(TestCase):
    """Tests for AI blog generation service."""
    
    def setUp(self):
        """Create test data."""
        self.user = User.objects.create_user(
            username='testadmin',
            email='admin@fammo.ai',
            password='testpass123'
        )
        
        self.topic = BlogTopic.objects.create(
            title="How to Train Your Puppy",
            language="en",
            primary_keyword="puppy training",
            secondary_keywords="dog training, puppy obedience",
            target_audience="New dog owners",
            status="TODO",
            priority=10
        )
        
        # Create some published posts for internal linking
        for i in range(3):
            BlogPost.objects.create(
                title=f"Published Post {i}",
                slug=f"published-post-{i}",
                content="Test content",
                language="en",
                is_published=True,
                published_at=timezone.now()
            )
    
    def test_get_internal_link_candidates(self):
        """Should retrieve published posts for internal linking."""
        candidates = get_internal_link_candidates('en', limit=5)
        
        self.assertEqual(len(candidates), 3)
        self.assertIn('title', candidates[0])
        self.assertIn('slug', candidates[0])
    
    def test_validate_ai_response_valid(self):
        """Should validate correctly structured response."""
        valid_response = {
            "blog": {
                "title": "Test",
                "slug": "test",
                "meta_description": "Test desc",
                "keywords": ["test"],
                "markdown": "# Test"
            },
            "internal_links": [],
            "external_links": [],
            "images": {
                "thumbnail": {"alt": "test", "prompt": "test"},
                "inline": []
            },
            "social": {
                "linkedin": {"text": "test", "hook": "test", "hashtags": []},
                "x": {"text": "test", "hashtags": []}
            }
        }
        
        is_valid, error = validate_ai_response(valid_response)
        
        self.assertTrue(is_valid)
        self.assertIsNone(error)
    
    def test_validate_ai_response_missing_key(self):
        """Should detect missing required keys."""
        invalid_response = {
            "blog": {},
            # Missing other required keys
        }
        
        is_valid, error = validate_ai_response(invalid_response)
        
        self.assertFalse(is_valid)
        self.assertIsNotNone(error)
    
    def test_format_social_drafts(self):
        """Should format social media drafts correctly."""
        response_data = {
            "social": {
                "linkedin": {
                    "text": "Great article about pets!",
                    "hashtags": ["PetCare", "FAMMO", "VetTech"]
                },
                "x": {
                    "text": "Check out our new blog post!",
                    "hashtags": ["Pets", "AI", "VetCare"]
                }
            }
        }
        
        linkedin_draft, x_draft = format_social_drafts(response_data)
        
        self.assertIn("Great article about pets!", linkedin_draft)
        self.assertIn("#PetCare", linkedin_draft)
        self.assertIn("#FAMMO", linkedin_draft)
        
        self.assertIn("Check out our new blog post!", x_draft)
        self.assertIn("#Pets", x_draft)
        self.assertIn("#AI", x_draft)
    
    @patch('blog.services.ai_blog_generator.get_openai_client')
    def test_generate_for_next_topic_success(self, mock_get_client):
        """Should successfully generate blog for next topic."""
        # Mock OpenAI response
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "blog": {
                "title": "How to Train Your Puppy: A Complete Guide",
                "slug": "train-your-puppy-complete-guide",
                "meta_description": "Learn effective puppy training techniques for new dog owners.",
                "keywords": ["puppy training", "dog training", "obedience"],
                "markdown": "# Introduction\n\nTraining your puppy is essential...\n\n## Basic Commands\n\n..."
            },
            "internal_links": [
                {"anchor": "published posts", "target_slug": "published-post-0", "placement_hint": "Introduction"}
            ],
            "external_links": [
                {"anchor": "AKC", "url": "https://akc.org", "placement_hint": "Resources section"}
            ],
            "images": {
                "thumbnail": {
                    "alt": "Cute puppy being trained",
                    "prompt": "Professional photo of a golden retriever puppy sitting attentively"
                },
                "inline": [
                    {
                        "alt": "Puppy learning commands",
                        "prompt": "Puppy responding to sit command",
                        "placement_hint": "Basic Commands section"
                    }
                ]
            },
            "social": {
                "linkedin": {
                    "text": "Training your puppy doesn't have to be hard! Our latest guide covers everything new dog owners need to know. Read more at https://fammo.ai/blog/train-your-puppy-complete-guide",
                    "hook": "Is your new puppy driving you crazy?",
                    "hashtags": ["PetCare", "DogTraining", "FAMMO", "PuppyLove"]
                },
                "x": {
                    "text": "New puppy? Master training basics with our complete guide 🐕 https://fammo.ai/blog/train-your-puppy-complete-guide",
                    "hashtags": ["Puppy", "DogTraining", "PetCare"]
                }
            }
        })
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client
        
        # Generate blog
        request = generate_for_next_topic('en', 'professional', self.user)
        
        # Verify request
        self.assertEqual(request.status, 'GENERATED')
        self.assertIsNotNone(request.blog_post)
        self.assertIsNotNone(request.generated_json)
        self.assertIsNotNone(request.linkedin_draft)
        self.assertIsNotNone(request.x_draft)
        
        # Verify blog post
        blog_post = request.blog_post
        self.assertFalse(blog_post.is_published)  # Should be draft
        self.assertEqual(blog_post.language, 'en')
        self.assertIn("Training your puppy", blog_post.title)
        
        # Verify topic status
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.status, 'COMPLETED')
        
        # Verify image suggestions
        image_suggestions = BlogPostImageSuggestion.objects.filter(post=blog_post)
        self.assertGreaterEqual(image_suggestions.count(), 2)  # At least thumbnail + 1 inline
        
        # Verify social drafts contain hashtags
        self.assertIn("#", request.linkedin_draft)
        self.assertIn("#", request.x_draft)
    
    @patch('blog.services.ai_blog_generator.get_openai_client')
    def test_generate_for_next_topic_failure_reverts_status(self, mock_get_client):
        """Should revert topic status on failure."""
        # Mock OpenAI to raise an exception
        mock_client = Mock()
        mock_client.chat.completions.create.side_effect = Exception("API Error")
        mock_get_client.return_value = mock_client
        
        # Attempt generation
        with self.assertRaises(Exception):
            generate_for_next_topic('en', 'professional', self.user)
        
        # Verify topic reverted to TODO
        self.topic.refresh_from_db()
        self.assertEqual(self.topic.status, 'TODO')
        self.assertIsNone(self.topic.last_used_at)
        
        # Verify request marked as FAILED
        request = BlogGenerationRequest.objects.first()
        self.assertEqual(request.status, 'FAILED')
        self.assertIn("API Error", request.error_message)
    
    def test_generate_for_next_topic_no_topics_raises_error(self):
        """Should raise ValueError when no TODO topics available."""
        # Mark all topics as completed
        BlogTopic.objects.update(status='COMPLETED')
        
        with self.assertRaises(ValueError) as cm:
            generate_for_next_topic('en', 'professional', self.user)
        
        self.assertIn("No TODO topics available", str(cm.exception))
    
    @patch('blog.services.ai_blog_generator.get_openai_client')
    def test_generate_handles_slug_collision(self, mock_get_client):
        """Should handle slug collisions by adding counter."""
        # Create existing post with slug
        BlogPost.objects.create(
            title="Existing",
            slug="train-your-puppy-guide",
            content="Test",
            language="en"
        )
        
        # Mock OpenAI response with same slug
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message.content = json.dumps({
            "blog": {
                "title": "Train Your Puppy Guide",
                "slug": "train-your-puppy-guide",  # Collision
                "meta_description": "Test",
                "keywords": ["test"],
                "markdown": "# Test"
            },
            "internal_links": [],
            "external_links": [],
            "images": {"thumbnail": {"alt": "test", "prompt": "test"}, "inline": []},
            "social": {
                "linkedin": {"text": "test", "hook": "test", "hashtags": []},
                "x": {"text": "test", "hashtags": []}
            }
        })
        
        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response
        mock_get_client.return_value = mock_client
        
        request = generate_for_next_topic('en', 'professional', self.user)
        
        # Should have added counter to slug
        self.assertNotEqual(request.blog_post.slug, "train-your-puppy-guide")
        self.assertTrue(request.blog_post.slug.startswith("train-your-puppy-guide"))


class ModelTests(TestCase):
    """Tests for model behaviors."""
    
    def test_blog_topic_str(self):
        """Should have meaningful string representation."""
        topic = BlogTopic.objects.create(
            title="Test Topic",
            language="en",
            status="TODO"
        )
        
        self.assertIn("Test Topic", str(topic))
        self.assertIn("en", str(topic))
        self.assertIn("TODO", str(topic))
    
    def test_blog_generation_request_str(self):
        """Should have meaningful string representation."""
        topic = BlogTopic.objects.create(title="Test", language="en", status="TODO")
        request = BlogGenerationRequest.objects.create(
            topic=topic,
            language="en",
            status="PENDING"
        )
        
        self.assertIn("Test", str(request))
        self.assertIn("PENDING", str(request))
    
    def test_blog_post_language_field(self):
        """Should have language field with proper choices."""
        post = BlogPost.objects.create(
            title="Test Post",
            slug="test-post",
            content="Test",
            language="tr"
        )
        
        self.assertEqual(post.language, "tr")
