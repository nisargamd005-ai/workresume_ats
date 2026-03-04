import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'workresume.settings')
django.setup()

from core.models import Application, Question

def fix_questions():
    # Fix all questions that have empty or broken options_json
    questions = Question.objects.all()
    print(f"DEBUG: Scanning {questions.count()} total questions.")
    
    fixed_count = 0
    demo_options = ["A) Option 1", "B) Option 2", "C) Option 3", "D) Option 4"]
    
    for q in questions:
        current_options = q.get_options()
        if not current_options or not isinstance(current_options, list):
            q.options_json = json.dumps(demo_options)
            q.save()
            print(f"DEBUG: Fixed Question ID {q.id} (was malformed or empty)")
            fixed_count += 1
            
    print(f"DEBUG: Done! Fixed {fixed_count} questions.")

if __name__ == '__main__':
    fix_questions()
