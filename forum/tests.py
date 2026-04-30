from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Question, Answer, Vote

User = get_user_model()


class ForumTestCase(TestCase):
    """Basic tests for forum functionality"""
    
    def setUp(self):
        self.user1 = User.objects.create_user(
            username='testuser1',
            email='test1@example.com',
            password='testpass123'
        )
        self.user2 = User.objects.create_user(
            username='testuser2',
            email='test2@example.com',
            password='testpass123'
        )
    
    def test_create_question(self):
        """Test creating a question"""
        question = Question.objects.create(
            title='Why is my dog not eating?',
            body='My dog has not eaten for 2 days',
            author=self.user1,
            category='dog_health'
        )
        self.assertEqual(question.title, 'Why is my dog not eating?')
        self.assertEqual(question.author, self.user1)
        self.assertFalse(question.is_answered)
    
    def test_create_answer(self):
        """Test creating an answer"""
        question = Question.objects.create(
            title='Test question',
            body='Test body',
            author=self.user1,
            category='general'
        )
        answer = Answer.objects.create(
            question=question,
            body='Test answer',
            author=self.user2
        )
        self.assertEqual(answer.question, question)
        self.assertEqual(answer.author, self.user2)
    
    def test_vote_count(self):
        """Test voting system"""
        question = Question.objects.create(
            title='Test question',
            body='Test body',
            author=self.user1,
            category='general'
        )
        # Initially no votes
        self.assertEqual(question.get_vote_count(), 0)
        
        # Add upvote
        # Note: Voting functionality will be tested via views
        # since it uses ContentType generic relations
