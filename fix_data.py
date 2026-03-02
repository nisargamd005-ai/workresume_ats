import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'workresume.settings')
django.setup()

from core.models import Application, Question

def fix_questions():
    # Fix all questions that have empty options_json
    questions = Question.objects.filter(options_json='')
    print(f"DEBUG: Found {questions.count()} questions with empty options.")
    
    # Generic fallback options
    demo_options = ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"]
    
    for q in questions:
        q.options_json = json.dumps(demo_options)
        q.save()
        print(f"DEBUG: Fixed Question ID {q.id}")

if __name__ == '__main__':
    fix_questions()
