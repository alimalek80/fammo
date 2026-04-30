from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q, Count
from django.http import JsonResponse
from django.contrib.contenttypes.models import ContentType
from django.views.decorators.http import require_POST

from .models import Question, Answer, Vote
from .forms import QuestionForm, AnswerForm


def question_list(request):
    """List all questions with filtering and search"""
    
    questions = Question.objects.all()
    
    # Search functionality
    search_query = request.GET.get('search', '')
    if search_query:
        questions = questions.filter(
            Q(title__icontains=search_query) | 
            Q(body__icontains=search_query)
        )
    
    # Category filter
    category = request.GET.get('category', '')
    if category:
        questions = questions.filter(category=category)
    
    # Sorting
    sort = request.GET.get('sort', 'recent')
    if sort == 'votes':
        # Annotate with vote counts (simplified for now)
        questions = questions.order_by('-created_at')  # Will improve this later
    elif sort == 'unanswered':
        questions = questions.filter(is_answered=False)
    else:  # recent
        questions = questions.order_by('-created_at')
    
    # Add answer and vote counts
    questions = questions.annotate(
        answer_count=Count('answers')
    )
    
    context = {
        'questions': questions,
        'search_query': search_query,
        'selected_category': category,
        'categories': Question.CATEGORY_CHOICES,
        'selected_sort': sort,
    }
    
    return render(request, 'forum/question_list.html', context)


def question_detail(request, pk):
    """View a single question with all its answers"""
    
    question = get_object_or_404(Question, pk=pk)
    
    # Increment view count
    question.views += 1
    question.save(update_fields=['views'])
    
    # Handle answer submission
    if request.method == 'POST' and request.user.is_authenticated:
        answer_form = AnswerForm(request.POST)
        if answer_form.is_valid():
            answer = answer_form.save(commit=False)
            answer.question = question
            answer.author = request.user
            answer.save()
            
            # Update question status
            if not question.is_answered:
                question.is_answered = True
                question.save(update_fields=['is_answered'])
            
            messages.success(request, 'Your answer has been posted!')
            return redirect('forum:question_detail', pk=pk)
    else:
        answer_form = AnswerForm()
    
    answers = question.answers.all()
    
    context = {
        'question': question,
        'answers': answers,
        'answer_form': answer_form,
    }
    
    return render(request, 'forum/question_detail.html', context)


@login_required
def ask_question(request):
    """Create a new question"""
    
    if request.method == 'POST':
        form = QuestionForm(request.POST, request.FILES)
        if form.is_valid():
            question = form.save(commit=False)
            question.author = request.user
            question.save()
            messages.success(request, 'Your question has been posted!')
            return redirect('forum:question_detail', pk=question.pk)
    else:
        form = QuestionForm()
    
    context = {
        'form': form,
    }
    
    return render(request, 'forum/ask_question.html', context)


@login_required
@require_POST
def vote(request, content_type, object_id, vote_type):
    """Handle upvote/downvote for questions and answers"""
    
    if content_type not in ['question', 'answer']:
        return JsonResponse({'error': 'Invalid content type'}, status=400)
    
    if vote_type not in ['up', 'down']:
        return JsonResponse({'error': 'Invalid vote type'}, status=400)
    
    # Get the model
    if content_type == 'question':
        model = Question
    else:
        model = Answer
    
    # Get the object
    try:
        obj = model.objects.get(pk=object_id)
    except model.DoesNotExist:
        return JsonResponse({'error': 'Object not found'}, status=404)
    
    # Prevent voting on own content
    if obj.author == request.user:
        return JsonResponse({'error': 'Cannot vote on your own content'}, status=400)
    
    # Get content type
    ct = ContentType.objects.get_for_model(model)
    
    # Check if user already voted
    existing_vote = Vote.objects.filter(
        user=request.user,
        content_type=ct,
        object_id=object_id
    ).first()
    
    if existing_vote:
        if existing_vote.vote_type == vote_type:
            # Remove vote if clicking same button
            existing_vote.delete()
            action = 'removed'
        else:
            # Change vote
            existing_vote.vote_type = vote_type
            existing_vote.save()
            action = 'changed'
    else:
        # Create new vote
        Vote.objects.create(
            user=request.user,
            content_type=ct,
            object_id=object_id,
            vote_type=vote_type
        )
        action = 'created'
    
    # Calculate new vote count
    vote_count = obj.get_vote_count()
    
    return JsonResponse({
        'success': True,
        'action': action,
        'vote_count': vote_count,
    })


@login_required
@require_POST
def accept_answer(request, answer_id):
    """Mark an answer as accepted (best answer)"""
    
    answer = get_object_or_404(Answer, pk=answer_id)
    question = answer.question
    
    # Only question author can accept answers
    if question.author != request.user:
        return JsonResponse({'error': 'Only question author can accept answers'}, status=403)
    
    # Remove previous accepted answer if any
    question.answers.update(is_accepted=False)
    
    # Mark this answer as accepted
    answer.is_accepted = True
    answer.save()
    
    # Update question status
    question.is_answered = True
    question.save()
    
    messages.success(request, 'Answer marked as accepted!')
    return redirect('forum:question_detail', pk=question.pk)
