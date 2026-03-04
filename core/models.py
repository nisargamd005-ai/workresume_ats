from django.db import models
from django.utils import timezone
import json

class Job(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    required_skills = models.TextField(help_text="Comma separated skills")
    min_match_score = models.IntegerField(default=60)
    test_threshold = models.IntegerField(default=70)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_skills_list(self):
        return [s.strip() for s in self.required_skills.split(",") if s.strip()]

class Candidate(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    resume = models.FileField(upload_to='resumes/')
    language = models.CharField(max_length=50, default='en')
    parsed_skills = models.TextField(blank=True)
    parsed_projects = models.TextField(blank=True)
    parsed_experience = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class Application(models.Model):
    STATUS_CHOICES = [
        ('PARSED', 'Parsed'),
        ('MATCHING', 'Matching'),
        ('TESTING', 'Testing'),
        ('PASSED', 'Passed'),
        ('FAILED', 'Failed'),
        ('REJECTED', 'Rejected'), # Matches < threshold
    ]
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    match_score = models.FloatField(default=0.0)
    test_score = models.FloatField(default=0.0)
    match_reasoning = models.TextField(blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PARSED')
    test_start_time = models.DateTimeField(null=True, blank=True)
    test_end_time = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.candidate.name} - {self.job.title}"

    def is_test_expired(self):
        if not self.test_start_time:
            return False
        # Limit to 10 minutes for now
        limit = timezone.now() - timezone.timedelta(minutes=10)
        return self.test_start_time < limit

class Question(models.Model):
    application = models.ForeignKey(Application, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()
    options_json = models.TextField(blank=True, default='[]') 
    correct_answer = models.CharField(max_length=50) # Increased for robustness
    candidate_answer = models.CharField(max_length=50, blank=True, null=True)

    def set_options(self, options_list):
        if not options_list:
            options_list = []
        self.options_json = json.dumps(options_list)
        self.save()

    def get_options(self):
        if not self.options_json:
            return []
        try:
            data = json.loads(self.options_json)
            if isinstance(data, dict):
                # Robustly handle {"A": "Choice A", ...}
                return [f"{k}) {v}" for k, v in data.items()]
            return data if isinstance(data, list) else []
        except:
            return []

