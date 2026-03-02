from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from .models import Candidate, Application, Job, Question
from .utils import extract_text_from_file, parse_resume_ai, evaluate_match_ai, generate_questions_ai
import json

def home(request):
    jobs = Job.objects.all()
    return render(request, 'home.html', {'jobs': jobs})

def apply_job(request, job_id):
    job = get_object_or_404(Job, id=job_id)
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        resume_file = request.FILES.get('resume')

        # 1. Create a NEW Candidate for every application to handle different resumes
        # No more get_or_create!
        candidate = Candidate.objects.create(
            name=name,
            email=email,
            resume=resume_file
        )

        # 2. Extract Text and Parse with AI
        resume_text = extract_text_from_file(candidate.resume.path)
        parsed_data = parse_resume_ai(resume_text)
        
        candidate.parsed_skills = parsed_data.get('skills', '')
        candidate.parsed_projects = parsed_data.get('projects', '')
        candidate.parsed_experience = parsed_data.get('experience', '')
        candidate.language = parsed_data.get('language', 'en')
        candidate.save()

        # 3. Job Role Matching
        match_data = evaluate_match_ai(parsed_data, job.required_skills)
        
        application = Application.objects.create(
            candidate=candidate,
            job=job,
            match_score=match_data.get('score', 0),
            match_reasoning=match_data.get('reasoning', ''),
            status='MATCHING'
        )

        # 4. Check Eligibility
        if application.match_score >= job.min_match_score:
            application.status = 'TESTING'
            application.save()
            
            # 5. Generate Test Questions
            try:
                questions_data = generate_questions_ai(parsed_data, job.title, candidate.language)
                for q in questions_data:
                    question = Question.objects.create(
                        application=application,
                        text=q.get('text'),
                        correct_answer=q.get('answer')
                    )
                    question.set_options(q.get('options', []))
            except Exception as e:
                print(f"Test Generation Failed: {e}")
        else:
            application.status = 'REJECTED'
            application.save()

        return redirect('application_result', app_id=application.id)

    return render(request, 'apply.html', {'job': job})

def application_result(request, app_id):
    application = get_object_or_404(Application, id=app_id)
    return render(request, 'matching_result.html', {
        'eligible': application.status == 'TESTING',
        'application': application,
        'match_score': application.match_score,
        'reasoning': application.match_reasoning
    })

def take_test(request, app_id):
    application = get_object_or_404(Application, id=app_id)
    
    if application.status != 'TESTING':
        return redirect('home')

    if not application.test_start_time:
        application.test_start_time = timezone.now()
        application.save()

    if application.is_test_expired():
        return redirect('evaluate_test', app_id=app_id)

    questions = application.questions.all()

    if request.method == 'POST':
        for q in questions:
            ans = request.POST.get(f'q_{q.id}')
            if ans:
                q.candidate_answer = ans
                q.save()
        
        return redirect('evaluate_test', app_id=app_id)

    return render(request, 'take_test.html', {
        'application': application, 
        'questions': questions,
        'time_limit': 10 # minutes
    })

def evaluate_test(request, app_id):
    application = get_object_or_404(Application, id=app_id)
    questions = application.questions.all()
    
    correct = 0
    total = questions.count()
    
    for q in questions:
        if q.candidate_answer == q.correct_answer:
            correct += 1
    
    score = (correct / total * 100) if total > 0 else 0
    application.test_score = score
    application.test_end_time = timezone.now()
    
    if score >= application.job.test_threshold:
        application.status = 'PASSED'
    else:
        application.status = 'FAILED'
    
    application.save()
    
    return render(request, 'test_result.html', {'application': application})

def company_dashboard(request):
    passed_applications = Application.objects.filter(status='PASSED').order_by('-test_score')
    all_applications = Application.objects.all().order_by('-created_at')
    
    total_count = all_applications.count()
    passed_count = passed_applications.count()
    selection_rate = (passed_count / total_count * 100) if total_count > 0 else 0

    return render(request, 'dashboard.html', {
        'passed_applications': passed_applications,
        'all_applications': all_applications,
        'selection_rate': selection_rate
    })

