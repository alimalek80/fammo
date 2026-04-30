# Forum App Documentation

## Overview
A Reddit-style Q&A forum for pet owners to ask questions and share knowledge.

## Features (Phase 1 - MVP)
✅ Ask questions about pet care
✅ Post answers to help others
✅ Upvote/downvote questions and answers
✅ Mark best answer (by question author)
✅ Category filtering (dog health, cat behavior, nutrition, etc.)
✅ Search questions
✅ Sort by recent, votes, or unanswered
✅ View counts
✅ User reputation (vote counts)

## URLs
- `/forum/` - List all questions
- `/forum/ask/` - Create new question (login required)
- `/forum/question/<id>/` - View question with answers
- `/forum/vote/<type>/<id>/<vote>/` - Vote on question/answer (AJAX)
- `/forum/answer/<id>/accept/` - Accept answer as best (POST)

## Models

### Question
- title (CharField) - Question title
- body (TextField) - Detailed description
- author (ForeignKey) - Question author
- category (CharField) - Category (dog_health, cat_health, nutrition, etc.)
- views (IntegerField) - View count
- is_answered (BooleanField) - Has accepted answer
- created_at, updated_at (DateTimeField)

### Answer
- question (ForeignKey) - Related question
- body (TextField) - Answer content
- author (ForeignKey) - Answer author
- is_accepted (BooleanField) - Marked as best answer
- created_at, updated_at (DateTimeField)

### Vote
- user (ForeignKey) - Voter
- vote_type (CharField) - 'up' or 'down'
- content_type (ForeignKey) - Generic relation (Question or Answer)
- object_id (PositiveIntegerField) - ID of voted item
- created_at (DateTimeField)

## Usage

### 1. Access the forum
Visit: `http://yoursite.com/en/forum/`

### 2. Ask a question (requires login)
1. Click "Ask Question" button
2. Fill in title, category, and detailed description
3. Submit

### 3. Answer a question (requires login)
1. Click on a question
2. Scroll to "Your Answer" section
3. Write your answer and submit

### 4. Vote
- Click up/down arrows on questions or answers
- Cannot vote on your own content
- Click again to remove your vote

### 5. Accept best answer (question author only)
- Click the ✓ button next to an answer
- Only one answer can be accepted
- Shows with green border and badge

## Admin Panel
Access at `/admin/` to:
- Moderate questions and answers
- Remove inappropriate content
- View vote statistics
- Manage categories

## Future Enhancements (Phase 2+)

### Easy to Add:
- Comments on answers
- Edit/delete your own posts
- User reputation points system
- Tags (multiple per question)
- Image uploads in questions
- Rich text editor (markdown)

### Medium Complexity:
- Notifications (when someone answers your question)
- Follow questions
- User badges/achievements
- Related questions suggestion
- Popular questions widget

### Advanced:
- AI-powered answer suggestions (using your ai_core)
- Duplicate question detection
- Auto-categorization of questions
- Community moderation (flag content)
- Analytics dashboard

## Testing
Run tests: `python manage.py test forum`

## Notes
- All dates use timezone-aware datetime
- AJAX voting requires CSRF token
- Generic relations used for flexible voting system
- Templates use Tailwind CSS + daisyUI (matching your design)
- Fully integrated with your existing user authentication
