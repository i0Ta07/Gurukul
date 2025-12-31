from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.utils import timezone
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator,MaxValueValidator,FileExtensionValidator
from django.contrib.auth.models import Permission
from django.contrib.auth.hashers import make_password, check_password
from functools import partial
import random,json
from django.db import IntegrityError
from datetime import timedelta
from scipy.stats import norm
import shortuuid







'''
                                DO NOT MAKE EXPLICIT ID'S NEXT TIME 
                                IF ORA INVALID IDENTIFIER ERROR GO FUCK WITH DATABASE
                                LEAVE THIS BS ALONE 
                                timestamp : 2:48 AM 06-04-2025

                                FROM NEXT TIME FOR CHOICES USE CLASS TYPECHOICES

'''

'''
User,Quiz,Question,Class,Result,Notes
one user can take many quiz 1:M
one quiz can have many questions 1:M
one user can join many classes 1:M
one user can access many notes 1:M
one class can have many notes 1:M
one user for one quiz have one result 1:1
opne class have many students having many results 1:M

many to one gives drop-down menu
many to many multiple select

user can have many classes 
class can have many users
many students can enroll in many classes M:N
many teacher can teach in many classes M:N

These classes represent database tables 
Create your models here.
instance of these class will reperesent a row in the table 
_before verbose lets it convert to different languaage we import packae above getextlazy
'''

# Validators

def validate_file_size(file, max_size_mb=5):
    max_size = max_size_mb * 1024 * 1024  # MB to Bytes
    if file.size > max_size:
        raise ValidationError(f"File size must be less than {max_size_mb}MB.")
    
# Access code 
import uuid

def generate_access_code(prefix, length=6):
    """
    prefix : str -> 1 char for object type like 'C', 'Q', 'N'
    length : int -> length of random part
    """
    chars = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ'
    
    def to_base36(num):
        res = ''
        while num:
            res = chars[num % 36] + res
            num //= 36
        return res or '0'

    # Generate a UUID and use its integer representation
    uid = uuid.uuid4().int  # Get the integer representation of the UUID
    code = to_base36(uid)[-length:].rjust(length, '0')  # Take the last `length` chars
    return f'{prefix.upper()}{code}'

def reset_access_code(obj):
    """
    obj : instance of any model having 'access_code' field.
    """
    if not hasattr(obj, 'access_code'):
        raise ValueError("Object has no access_code field")

    obj.access_code = ''
    obj.save()


class User(AbstractUser):
    USER_TYPE_CHOICES = [
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    ]
    TITLE_TYPE_CHOICES = [
        ('Mr.','Mr.'), #stored in database,human readable
        ('Mrs.','Mrs.'),
        ('Miss.','Miss.'),
        ('Ms.','Ms.'),
        ('Dr.','Dr.'),
    ]

    title = models.CharField(
        max_length=10,
        choices=TITLE_TYPE_CHOICES,
        default='Mr.'
    )
    phone_number = models.CharField(max_length=15)
    date_of_birth = models.DateField()
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default='student',
    )
    friends = models.ManyToManyField('self', through='Friend')
    # If your Friend model already ensures both-way friendship on ACCEPTED — you're good. IMP
    #class meta to define table name ,to specify default ordering 
    profile_photo = models.ImageField( 
        default='profile_photos/default.png',
        upload_to='profile_photos/',
        help_text="Upload a profile picture"
    )
    class Meta:
        db_table = 'User' # set the table name to User this is migrations.AlterModelTable
        verbose_name = _('user')
        verbose_name_plural = _('users')
        ordering = ['last_name', 'first_name']


    def save(self, *args, **kwargs):
        # Call the clean method to validate the model instance
        # Call the original save method to ensure the user is saved
        super().save(*args, **kwargs)
        # Assign permissions based on user type for new users
        '''is_new_user = self.pk is None
        if is_new_user:
            if self.user_type == 'teacher':
                permissions = Permission.objects.filter(codename__in=[
                    'add_announcement', 'change_announcement', 'delete_announcement', 'view_announcement',
                    'view_answer',
                    'add_class', 'change_class', 'delete_class', 'view_class',
                    'add_notes', 'change_notes', 'delete_notes', 'view_notes',
                    'add_question', 'change_question', 'delete_question', 'view_question',
                    'add_quiz', 'change_quiz', 'delete_quiz', 'view_quiz',
                    'view_result',
                    'view_user',
                ])
                self.user_permissions.add(*permissions)

            # Automatically assign permissions if the user is a student
            elif self.user_type == 'student':
                permissions = Permission.objects.filter(codename__in=[
                    'add_announcement', 'change_announcement', 'delete_announcement', 'view_announcement',
                    'add_answer', 'view_answer',
                    'view_class',
                    'add_notes', 'change_notes', 'delete_notes', 'view_notes',
                    'view_question',
                    'view_quiz',
                    'view_result',
                    'view_user',
                ])
                self.user_permissions.add(*permissions)'''
    def __str__(self):
        return f"{self.title} {self.first_name} {self.last_name} ({self.user_type})"

class Friend(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = 'pending'
        ACCEPTED = 'accepted'
        # No rejected we ddelete the relationship object if rejected

    from_user = models.ForeignKey(User, related_name='from_people', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='to_people', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
        

    class Meta:
        ordering = ['-created_at']

    def clean(self):
        if self.from_user == self.to_user:
            raise ValidationError("You cannot add yourself as a friend.")

    def __str__(self):
        return f"{self.from_user} - {self.to_user}"
    
    def save(self, *args, **kwargs):
        self.full_clean() 
        super().save(*args, **kwargs)


class Quiz(models.Model):
    ACCESS_TYPE_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]
    QUIZ_TYPE_CHOICES = [
        ('objective', 'MCQ / True-False (Auto Evaluation)'),
        ('objective_and_subjective', 'MCQ / True-False / Text (Mixed)'),
    ]

    quiz_id = models.CharField(
        max_length=50,
        primary_key=True,
        editable=False,
        verbose_name=_('Quiz ID'),
        help_text=_('Unique identifier for the quiz, combines "K", user_id, and an incrementing number')
    )
    name = models.CharField(max_length=255, verbose_name=_('Quiz Name'),help_text='Subject : Topic Example : Java: AWT Classes')
    created_by = models.ForeignKey(
        'User',  # Refers to your custom User model
        on_delete=models.CASCADE,
        related_name='quizzes',
        verbose_name=_('Created By'),
        limit_choices_to={'user_type': 'teacher'},
    )
    description = models.TextField(blank=True, verbose_name=_('Description'))
    access_code = models.CharField(
        max_length=7,  
        blank=True,
        unique=True,
        verbose_name=_('Access Code'),
        help_text=_('Access code required for private quiz')
    )
    access_type = models.CharField(
        max_length=10,
        choices=ACCESS_TYPE_CHOICES,
        default='public',
        verbose_name=_('Access Type')
    )
    quiz_type = models.CharField(
        max_length=25,
        choices=QUIZ_TYPE_CHOICES,
        default='objective',
        verbose_name=_('Quiz Type'),
        help_text=_('Select the type of questions for this quiz')
    )
    #can uplaod quiz file for ease
    # have to dynamically load question related to specific quiz
    

    # Assign quiz to many classes
    assigned_classes = models.ManyToManyField(
        'Class',  # Refers to your Class model
        related_name='quizzes',
        blank=True,
        verbose_name=_('Assigned Classes'),
        help_text=_('Classes to which this quiz is assigned')
    )
    
    # Assign quiz to many students (users)
    #can be assigned by teachers to students like those are of private 
    assigned_to = models.ManyToManyField(
        'User',  # Refers to the User model
        related_name='assigned_quizzes',
        blank=True,
        verbose_name=_('Quiz Assigned To User'),
        help_text=_('Users to whom this quiz is assigned'),
    )
    # deleted because we dont want teacher to explicitely give permission
    # for a quiz to student he can access it using access code

    

    #even teacher can save quiz to redit to evaluate 
    quiz_saved_by_users = models.ManyToManyField(
        'User', 
        related_name='quiz_saved_by_users', 
        blank=True,
        verbose_name=_('Saved by users'),
        help_text=_('Users who saved this quiz'),
    )
    
    weighted_score_avg = models.FloatField(
        default=0.0,
        verbose_name=_("Weighted Score Average"),
        help_text=_("Average of recent weighted scores")
    )

    weighted_score_std_dev = models.FloatField(
        default=0.0,
        verbose_name=_("Weighted Score Standard Deviation"),
        help_text=_("Standard deviation of recent weighted scores")
    )
    max_marks = models.FloatField(
        null=True,
        blank=True,
        verbose_name=_('Total Marks'),
    )
    min_marks = models.FloatField(
        null=True,
        blank=True,
        verbose_name=_('Minimum Marks'),
    )
    min_duration = models.FloatField(
        default=0.0,
        verbose_name=_('Minimum Duration'),
    )
    total_attempts = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Total Attempts'),
        help_text=_('Total number of attempts made for this quiz')
    )
    history_limit = models.PositiveIntegerField(
        default=1000,  # Default to 1000 entries
        verbose_name=_("History Limit"),
        help_text=_("Number of recent weighted scores to keep for calculating averages")
    )
    
    score_history = models.JSONField(
        default=list,  # Store recent weighted scores
        verbose_name=_(" Scores History"),
        blank=True,
        help_text=_("List of recent weighted scores and ac used for calculating averages")
    )
    start_time = models.DateTimeField(
        default=now,
        verbose_name=_('Start Time'),
        help_text=_('Time when the quiz becomes available for responses')
    )
    end_time = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('End Time'),
        help_text=_('Time after which the quiz will stop accepting responses')
    )
    rating = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Quiz Rating'),
        help_text=_('Average rating of this quiz out of 5 stars'),
        validators=[MinValueValidator(0)]
    )
    total_ratings = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Total Ratings'),
        help_text=_('Total number of ratings given for this quiz')
    )
    weight_marks = models.FloatField(
        default=0.5,
        verbose_name=_("Weight for Marks"),
        help_text=_("Weight given to marks in weighted score calculation"),
        validators=[MinValueValidator(0),MaxValueValidator(1)]
    )

    weight_duration = models.FloatField(
        default=0.5,
        verbose_name=_("Weight for Duration"),
        help_text=_("Weight given to duration in weighted score calculation"),
        validators=[MinValueValidator(0),MaxValueValidator(1)]
    )
    
    time_limit = models.DurationField(default=timedelta(minutes=30),  verbose_name=_('Time Limit'), help_text=_('Time limit for the quiz in hours, minutes, and seconds'))
    created_at = models.DateTimeField(auto_now_add=True,verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True,verbose_name=_('Updated At'))
    is_active = models.BooleanField(default=True, verbose_name=_('Is Active'))

    
    class Meta:
        verbose_name = _('Quiz')
        verbose_name_plural = _('Quizzes')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} - {self.created_by.title} {self.created_by.first_name} {self.created_by.last_name}"

    def update_rating(self, new_rating):
        """
        Incrementally update the quiz rating when a new rating is added.
        """
        print("Enterred update raing ")
        new_total = self.total_ratings + 1
        self.rating = ((self.rating * self.total_ratings) + new_rating) / new_total
        self.total_ratings = new_total
        self.rating = round(self.rating, 2)  # Keep it clean
        self.save(update_fields=['rating', 'total_ratings'])

    def save(self, *args, **kwargs):
        """
        Override save method to generate quiz_id in the format 'K<user_id>-<increment>'.
        """
        if not self.quiz_id:
            # Generate the notes_id as a combination of "N", username and creation timestamp
            created_timestamp = now().strftime('%f-%S-%M-%H-%d-%m-%Y')  # Format the timestamp part
            self.quiz_id = f"K_{self.created_by.username}-{created_timestamp}"
        
        if not self.access_code:
            while True:
                self.access_code = generate_access_code('Q')
                try:
                    super().save(*args, **kwargs)
                    break
                except IntegrityError:
                    continue  # regenerate and try again
        else:
            super().save(*args, **kwargs)

    def is_available(self):
        """Check if the quiz is currently available for taking responses."""
        current_time = now()
        
        # Check if the quiz is within the start and end time range
        if self.start_time and current_time < self.start_time:
            return False
        if self.end_time and current_time > self.end_time:
            return False
        
        return True

    def update_stats(self, new_score, new_duration):
        """
        Updates statistics including total attempts, weighted score, and standard deviation.
        """
        # Store the old mean values
        old_mean_weighted = self.weighted_score_avg

        # Increment total attempts
        self.total_attempts += 1

        # Calculate the new weighted score (default weights: 0.5 for marks, 0.5 for duration)
        total_seconds = int(self.time_limit.total_seconds())
        normalized_marks = (new_score- self.min_marks)/(self.max_marks - self.min_marks)
        normalized_duration = 1 - ((new_duration  - self.min_duration)/ (total_seconds - self.min_duration))
        print(normalized_marks,normalized_duration)
        new_weighted_score = ((self.weight_marks * normalized_marks) + (self.weight_duration * normalized_duration)) * 100

        # Maintain score_history (keep only latest history_limit entries)
        if len(self.score_history) == self.history_limit:
            oldest_entry = self.score_history.pop(0)
            oldest_weighted_score = oldest_entry['weighted_score']
            
            self.weighted_score_avg = (self.weighted_score_avg * self.history_limit - oldest_weighted_score + new_weighted_score) / self.history_limit
        
        else:
            n = len(self.score_history) + 1
            self.weighted_score_avg = ((self.weighted_score_avg * (n - 1)) + new_weighted_score) / n
        
        # Append new weighted score
        self.score_history.append({'marks_scored': new_score, 'weighted_score': new_weighted_score})

        # Compute standard deviation for weighted scores
        n = len(self.score_history)
        if n > 1:
            self.weighted_score_std_dev = (((n - 1) * (self.weighted_score_std_dev ** 2) + (new_weighted_score - old_mean_weighted) * (new_weighted_score - self.weighted_score_avg)) / n) ** 0.5
        else:
            self.weighted_score_std_dev = 0.0

        # Save only updated fields
        self.save(update_fields=[
            "total_attempts", 
            "weighted_score_avg", 
            "weighted_score_std_dev", 
            "score_history"
        ])


class Question(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('mcq', 'Multiple Choice Question'),
        ('text', 'Text Response'),
        ('true_false', 'True/False Question'),
    ]

    question_id = models.CharField(
        max_length=100,
        primary_key=True,
        editable=False,
        verbose_name=_('Question ID'),
        help_text=_('Unique identifier for the question, combines "Q", quiz_id, and an incrementing number')
    )
    quiz = models.ForeignKey(
        'Quiz',
        on_delete=models.CASCADE,
        related_name='questions',
        verbose_name=_('Quiz'),
        help_text=_('The quiz to which this question belongs')
    )
    question_type = models.CharField(
        max_length=10,
        choices=QUESTION_TYPE_CHOICES,
        verbose_name=_('Question Type'),
        default='mcq',
        help_text=_('The type of question: MCQ, Text-(Long or Short), or True/False')
    )
    question_text = models.TextField(
        verbose_name=_('Question Text'),
        help_text=_('The text of the question'),
        null=False,
    )
    question_image = models.ImageField(
        upload_to='question_images/',
        blank=True,
        null=True,
        verbose_name=_('Image'),
        help_text=_('Optional image related to the question'),
        validators=[validate_file_size,FileExtensionValidator(allowed_extensions=[ 'png', 'jpeg']),]
    )
    remarks = models.TextField(
        blank=True,
        verbose_name=_('Remarks'),
        help_text=_('Explanation or remarks on why the option is correct')
    )
    options = models.JSONField(
        default=list,
        verbose_name=_('Options'),
        help_text=_('JSON object containing options for MCQ and True/False Example ["Paris", "London", "Berlin", "Rome"] ')
    )
    correct_option = models.TextField(
        blank=True,
        verbose_name=_('Correct Option'),
        help_text=_('The correct answer (applicable for MCQ and True/False questions) Example : Paris or True')
    )
    marks = models.IntegerField(
        verbose_name=_('Marks'), default=1,
        help_text=_('Marks allocated for this question')
    )
    negative_marks = models.FloatField(
        verbose_name=_('Negative Marks'),
        default=0.0,
        help_text=_('Marks deducted for an incorrect answer')
    )
    success_rate = models.JSONField(
        default=dict,
        verbose_name=_('Success Rate'),
        help_text=_('Tracks attempts and correct answers, e.g., {"attempts": 0, "correct": 0}')
    )

    created_at = models.DateTimeField(auto_now_add=True,verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Question')
        verbose_name_plural = _('Questions')
        ordering = ['quiz', 'question_id']

    def __str__(self):
        formatted_date = self.created_at.strftime('%d-%m-%y %H:%M')  # dd-mm-yy HH:MM
        return f"{self.quiz.name} - {formatted_date} ({self.get_question_type_display()})"
    
    def clean(self):
        # Ensure question type is valid based on quiz type
        if self.quiz.quiz_type == 'objective' and self.question_type == 'text':
            raise ValidationError(_("Objective quizzes can only contain MCQ or True/False questions."))
        

    def save(self, *args, **kwargs):
        # Automatically set the question_id before saving the instance
        if not self.question_id:
            # Generate the notes_id as a combination of "N", username and creation timestamp
            created_timestamp = now().strftime('%f-%S-%M-%H-%d-%m-%Y')  # Format the timestamp part
            # Generate the unique question_id
            self.question_id = f"Q_{self.quiz.quiz_id}-{created_timestamp}"
        self.full_clean() 
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        if self.question_image:
            self.question_image.delete(save=False)
        if self.question_type == 'text':
            self.quiz.text_questions_ids.remove(self.question_id)
            self.quiz.save()
        super().delete(*args, **kwargs)

    def shuffle_options(self):
        """Shuffle the options for MCQ and True/False questions and save them."""
        if self.question_type in ['mcq', 'true_false'] and self.options:
            shuffled_options = self.options[:]  # Creates a shallow copy of self.options to avoid unexpected side effects
            random.shuffle(shuffled_options)
            self.options = shuffled_options  
            self.save(update_fields=['options'])  
    

    
    '''
    quiz_instance = Quiz.objects.get(id=1)  # Assume a quiz already exists
    question = Question.objects.create(
    quiz=quiz_instance,
    text="What is the capital of France?",
    question_type="mcq",
    options=["Paris", "London", "Berlin", "Rome"], JSON format
    correct_answer=Paris,
    points=5
    # Get all questions for a specific quiz
    questions = quiz_instance.questions.all()

    for question in questions:
        print(question.text, question.points)

    '''


class Answer(models.Model):
    # Answer ID: Combines question_id and username, starts with 'A_'
    answer_id = models.CharField(max_length=255, primary_key=True, editable=False)

    # ForeignKey to Quiz
    quiz = models.ForeignKey('Quiz', on_delete=models.CASCADE, related_name='answers')

    # ForeignKey to Question
    question = models.ForeignKey('Question', on_delete=models.CASCADE, related_name='answers')

    # ForeignKey to User (who is taking the quiz)
    answered_by = models.ForeignKey('User', on_delete=models.CASCADE, related_name='quiz_answers',
    limit_choices_to={'user_type': 'student'},)

    # Already NOT NULL but cannot remove from here
    attempt = models.ForeignKey('Attempt', on_delete=models.CASCADE, related_name='attempt', null=True) 

    # The user's submitted answer (for MCQ or True/False)
    selected_option = models.CharField(max_length=255, blank=True)  # For MCQ or True/False

    # The user's submitted text answer (for short or long answers)
    text_answer = models.TextField(blank=True)

    # Tracks if the answer has been reviewed (useful for manually graded quizzes)
    is_reviewed = models.BooleanField(default=False)

    # Points scored for this question
    marks_scored = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)

    # When the answer was submitted
    answered_at = models.DateTimeField(auto_now_add=True)


    def save(self, *args, **kwargs):
        """
        Custom save method to generate `answer_id` dynamically.
        The ID format will be: 'A_<quiz_id>_<question_id>_<username>'
        """
        if not self.answer_id:
            self.answer_id = f"A_{self.question.question_id}_{self.answered_by.username}"
        super().save(*args, **kwargs)

    def evaluate(self):
        """
        Evaluate the answer for correctness and assign marks (if auto-gradable).
        """
        if self.question.question_type in ['mcq', 'true_false']:
            if self.selected_option == self.question.correct_option:
                self.marks_scored = self.question.marks
            else:
                self.marks_scored = -abs(self.question.negative_marks or 0)
            self.is_reviewed = True
        self.save()
        
    def __str__(self):
        formatted_date = self.answered_at.strftime('%d-%m-%y %H:%M')  # dd-mm-yy HH:MM
        return f"{self.quiz.name} by {self.answered_by.username} at {formatted_date}"

    class Meta:
        verbose_name = "Answer"
        verbose_name_plural = "Answers"
        unique_together = ('quiz', 'question', 'answered_by')  # Ensures no duplicate answers
        ordering = ['answered_at']  # Orders by the time of submission

    #if for specific java change it to students


class Attempt(models.Model):
    COMPLETION_REASON_CHOICES = [
        ('timeout', 'Time Ran Out'),
        ('manual_submit', 'User submitted manually'),
        ('cheating','Cheating Detected')
    ]
    STATUS_CHOICES = [
        ('passed', 'Passed'),
        ('failed', 'Failed'),
        ('pending', 'Pending'),
    ]
    attempt_id = models.CharField(
        max_length=255,
        primary_key=True,
        editable=False,
        verbose_name=_('Attempt ID'),
        help_text=_('Unique identifier for the attempt, combining quiz_id, username, and timestamp')
    )
    
    user = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name="attempts",
        verbose_name=_('User'),
        help_text=_('User attempting the quiz')
    )
    quiz = models.ForeignKey(
        'Quiz',
        on_delete=models.CASCADE,
        related_name="attempts",
        verbose_name=_('Quiz'),
        help_text=_('Quiz being attempted')
    )
    marks_scored = models.FloatField(
        default=0.0,
        verbose_name=_('Marks Scored'),
        help_text=_('Marks scored by the user in this attempt')
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name=_('Status'),
        help_text=_('The status of the result: Passed, Failed, or Pending')
    )
    attempt_time = models.DateTimeField(
        verbose_name=_('Attempt Time'),
        help_text=_('Timestamp when the attempt started')
    )
    completed_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_('Completed At'),
        help_text=_('Timestamp when the attempt was completed')
    )
    end_time = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_(' Quiz End Time'),
        help_text=_('Quiz end time decided when the user start the quiz')
    ) 
    # duration should be duration field
    duration = models.FloatField(
        blank=True,
        null=True,
        verbose_name=_('Duration'),
        help_text=_('Time taken to complete the quiz'),
        validators=[MinValueValidator(0)]
    )
    review_not_answered = models.JSONField(default=list, blank=True)
    review_but_answered = models.JSONField(default=list, blank=True)
    weighted_score = models.FloatField(default=0.0)  
    percentile_weighted_score = models.FloatField(default=0.0)
    remaining_time = models.FloatField(
        verbose_name=_('Remaining Time'),
        help_text=_('Remaining time left in the quiz'),
    )
    reload = models.IntegerField(default=0)
    completion_reason = models.CharField(
        max_length=15,
        choices=COMPLETION_REASON_CHOICES,
        blank=True,
        verbose_name=_('Completion Reason'),
        help_text=_('Reason why the quiz was completed')
    )
    current_question_index = models.IntegerField(
        default=0,
        verbose_name=_('current question index'),
        help_text=_('The questions index on which the user is on, starts with 0')
    )
    question_order = models.JSONField(default=list)  # Store shuffled question indexes as a list
    rating = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Attempt Rating'),
        help_text=_('Rating given by the user for this attempt (out of 5 stars)'),
        validators=[MinValueValidator(0),MaxValueValidator(5)]
    )
    feedback = models.TextField(
        blank=True,
        verbose_name=_('Feedback'),
        help_text=_('Feedback or comments for the student on the result')
    )
    wrong_notAttempted = models.JSONField(
        default=list,
        blank=True,
    )
    question_status = models.JSONField(default=dict)  # Stores question status dict answered and marked_for_review only

    def shuffle_questions(self):
        """Shuffle questions once and store the order."""
        question_ids = list(self.quiz.questions.values_list('question_id', flat=True))
        random.shuffle(question_ids)
        self.question_order = question_ids  
        self.save(update_fields = ['question_order'])

    
    #called in start quiz
    def finalize(self,status):
        """
        Helper function to complete the quiz, mark it as finished, and evaluate the attempt.
        """
        self.completed_at = now()
        self.completion_reason = status
        if status == 'manual_submit':
            self.duration = (self.completed_at - self.attempt_time).total_seconds()
        elif status in ['timeout','cheating']:
            self.duration = self.quiz.time_limit.total_seconds()

        # Evaluate the attempt and calculate marks
        self.evaluate_attempt()
        
        # Save only the relevant fields for the attempt
        self.save(update_fields=["completed_at", "completion_reason", "duration"])

        if self.quiz.quiz_type == 'objective':
            self.quiz.update_stats(new_score=self.marks_scored, new_duration=self.duration)
            self.weighted_score = self.quiz.score_history[-1]['weighted_score']
            self.save(update_fields=['weighted_score'])
        
        
        if self.quiz.min_duration == 0 or self.duration < self.quiz.min_duration:
            self.quiz.min_duration = self.duration
            self.quiz.save(update_fields=['min_duration'])
        
        self.calculate_weighted_percentile()
        
    #Not needed
    def get_current_question(self, question_index):
        """
        Fetch the question based on the shuffled order and given index.
        _question_ids is a cached attribute used to track the current shuffled order
        This prevents reloading the order every time and reduces the frequency of times we access the database

        """
        if not hasattr(self, '_question_ids'):
            self._question_ids = self.question_order

        # Ensure index is within bounds
        if question_index >= len(self._question_ids):
            raise IndexError(f"Question index {question_index} out of range for quiz {self.quiz.quiz_id}")

        return self.quiz.questions.get(question_id=self._question_ids[question_index])

      
    
    def evaluate_attempt(self):
        """Evaluates all answers for this attempt and calculates the score."""
        wrong_not_attempted_questions = []
        answers = Answer.objects.filter(attempt=self)
        attempted_questions = set()

        #Checking Answers
        for answer in answers:
            attempted_questions.add(answer.question.question_id)
            if answer.question.question_type != 'text':
                answer.evaluate()
                self.marks_scored += answer.marks_scored
                question = answer.question
                question.success_rate['attempts'] = question.success_rate.get('attempts', 0) + 1
                if answer.marks_scored > 0:
                    question.success_rate['correct'] = question.success_rate.get('correct', 0) + 1
                question.save(update_fields=['success_rate'])
                if answer.marks_scored <= 0:
                    wrong_not_attempted_questions.append(answer.question.question_id) #wrong questions

        # Identify unattempted questions
        all_questions = set(self.quiz.questions.values_list('question_id', flat=True))
        unattempted_questions = all_questions - attempted_questions
        wrong_not_attempted_questions.extend(unattempted_questions) #wrong + unattemptetd

        self.wrong_notAttempted = wrong_not_attempted_questions
        self.save(update_fields=['marks_scored', 'wrong_notAttempted'])

    def calculate_weighted_percentile(self):
        """Calculates percentile rank for the weighted score in the attempt."""
        quiz = self.quiz  
        z_score_weighted = 0

        # Calculate Z-score for Weighted Score
        print(type(quiz.weighted_score_avg),type(quiz.weighted_score_std_dev),type(self.weighted_score))
        if quiz.weighted_score_std_dev > 0:
            z_score_weighted = (self.weighted_score - quiz.weighted_score_avg) / quiz.weighted_score_std_dev

        # Convert Z-score to Percentile Rank
        self.percentile_weighted_score = 50.0 if z_score_weighted == 0 else round(norm.cdf(z_score_weighted) * 100, 2)

        # Save the changes
        self.save(update_fields=['percentile_weighted_score'])

    def save(self, *args, **kwargs):
        """
        Override save method to dynamically generate `attempt_id`.
        Format: A_<username>_<quiz_id>_<timestamp>.
        Also calculates `duration` if `completed_at` is set.
        """
        if not self.attempt_id:
            created_timestamp = now().strftime('%f-%S-%M-%H-%d-%m-%Y')
            self.attempt_id = f"AT_{self.user.username}_{self.quiz.quiz_id}_{created_timestamp}"

        # Ensure remaining time doesn't go negative
        if self.remaining_time is not None and self.remaining_time < 0:
            self.remaining_time = None
        
        super().save(*args, **kwargs)

    def __str__(self):
        formatted_date = self.completed_at.strftime('%d-%m-%y %H:%M')  # dd-mm-yy HH:MM
        return f"{self.user.username} - {self.quiz.name} - {formatted_date}"

    
    class Meta:
        verbose_name = _('Attempt')
        verbose_name_plural = _('Attempts')
        ordering = ['-attempt_time']



class Class(models.Model):
    ACCESS_TYPE_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]

    class_id = models.CharField(
        max_length=255,
        primary_key=True,
        editable=False,
        verbose_name=_('Class ID'),
        help_text=_('Unique identifier for the class, combines "C", username of the creator, and an incrementing number')
    )
    name = models.CharField(max_length=255, verbose_name=_('Class Name'),help_text='Subject + Class Example(Java MCA-1)')
    created_by = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='created_classes',
        verbose_name=_('Created By'),
        help_text=_('Teacher who created the class'),
        limit_choices_to={'user_type': 'teacher'},
    )
    students = models.ManyToManyField(
        'User',
        related_name='enrolled_students',
        verbose_name=_('Students'),
        blank=True,
        help_text=_('Students enrolled in this class'),
        limit_choices_to={'user_type': 'student'},
    )
    teachers = models.ManyToManyField(
        'User',
        #settings.AUTH_USER_MODEL,  # Linking to the User model (teachers)
        related_name='class_teachers',
        verbose_name=_('Teachers'),
        help_text=_('Teachers assigned to this class'),
        limit_choices_to={'user_type': 'teacher'},
    )
    
    description = models.TextField(
        blank=True,
        verbose_name=_('Class Description'),
        help_text=_('A brief description of the class including objectives and syllabus')
    )
    current_topic = models.CharField(
        blank=True,
        verbose_name=_('Current Topic'),
        help_text=_('Current topic of the class'),
        max_length=255
    )
    last_topic = models.CharField(
        blank=True,
        verbose_name=_('last Topic'),
        help_text=_('last topic of the class'),
        max_length=255
    )
    next_topic = models.CharField(
        blank=True,
        verbose_name=_('next Topic'),
        help_text=_('next topic of the class'),
        max_length=255
    )
    next_class_date = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=('Next Class Date and Time'),
        help_text=('Date and Time when the class is gonna be '),
    )
    next_class_teacher = models.ForeignKey(
        'User',
        blank=True,
        null=True,
        on_delete=models.SET_NULL,
        related_name='next_class_teacher',
        verbose_name=_('next_class_teacher'),
        help_text=_('Teacher who will take the next scheduled class'),
        limit_choices_to={'user_type': 'teacher'},
    )
    # Already  NOT NULL as default = list but cannot remove it from here.
    textbooks = models.JSONField(
        default=list, 
        null=True,
        blank=True,
        verbose_name=_('textbooks'),
        help_text=_('Store multiple textbook names in JSON format as a list. ["Alice", "Bob", "Charlie", "David"]')
    )
    book_used_class = models.ManyToManyField(
        'Book',
        related_name='Class',
        verbose_name=_('book_used_class'),
        blank = True,
        help_text=_('Textbook of the class, specify if it is in the library')
    )
    max_students = models.PositiveIntegerField(
        default=30,
        verbose_name=_('Maximum Students'),
        help_text=_('Maximum number of students allowed in this class')
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_('Is Active'),
        help_text=_('Indicates whether the class is currently active')
    )
    schedule = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('Schedule'),
        help_text=_('Class schedule in JSON format. Example: ["9 AM","None","12 PM","2 PM","None","10 AM","None"]')
    )

    syllabus_file = models.FileField(
        upload_to='syllabus_files/',
        blank=True,
        null=True,
        verbose_name=_('Syllabus (File)'),
        help_text=_('Upload the syllabus as a file (PDF or other formats).'),
        validators=[FileExtensionValidator(allowed_extensions=[ 'pdf', 'docx','txt','doc']),validate_file_size]
    )
    access_type = models.CharField(
        max_length=7,
        choices=ACCESS_TYPE_CHOICES,
        default='public',
        verbose_name=_('Access Type'),
        help_text=_('Class access type: Public or Private')
    )
    access_code = models.CharField(
        max_length=7,
        blank=True,
        unique=True,
        verbose_name=_('Access Code'),
        help_text=_('Access code required for private class enrollment')
    )
    
    created_at = models.DateTimeField(auto_now_add=True , verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True ,verbose_name=_('Updated At'))

    class Meta:
        verbose_name = _('Class')
        verbose_name_plural = _('Classes')
        ordering = ['-created_at']

    
    def __str__(self):
        return f"{self.name} - {self.created_by.title} {self.created_by.first_name} {self.created_by.last_name}"
        

    def save(self, *args, **kwargs):
        # Automatically set the class_id before saving the instance
        if not self.class_id:
            created_timestamp = now().strftime('%f-%S-%M-%H-%d-%m-%Y')  # Format the timestamp part
            self.class_id = f"C_{self.created_by.username}-{created_timestamp}"

        if not self.access_code:
            while True:
                self.access_code = generate_access_code('C')
                try:
                    super().save(*args, **kwargs)
                    break  # success
                except IntegrityError:
                    continue  # regenerate access_code and try again
        else:
            super().save(*args, **kwargs)
        

    
    def delete(self, *args, **kwargs):
        """Override delete to ensure file attachments are also removed."""
        if self.syllabus_file:
            self.syllabus_file.delete(save=False)
        super().delete(*args, **kwargs)

    
'''
Notes are default public and can be accessed by either class they belong to or the common public 
by search.
'''
class Notes(models.Model):
    ACCESS_TYPE_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]

    notes_id = models.CharField(
        max_length=100,
        primary_key=True,
        editable=False,
        verbose_name=_('Notes ID'),
        help_text=_('Unique identifier for the notes, combines "N", username of creator and creation timestamp')
    )
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    created_by = models.ForeignKey(
        'User',
        on_delete=models.CASCADE,
        related_name='created_notes',
        verbose_name=_('Created By'),
        help_text=_('The user who created this note (likely a teacher or admin)')
    )
    access_code = models.CharField(
        max_length=7,  # Increased size to accommodate hashed values
        blank=True,
        unique=True,
        verbose_name=_('Access Code'),
        help_text=_('Access code required for private notes')
    )
    access_type = models.CharField(
        max_length=7,
        choices=ACCESS_TYPE_CHOICES,
        default='public',
        verbose_name=_('Access Type'),
        help_text=_('Type of access: Public or Private')
    )
    topic = models.CharField(max_length=100, help_text="Parent/related topic of the notes")
    class_belongs_to= models.ManyToManyField(
        'Class',  # Refers to your Class model
        blank=True,
        related_name='notes',
        verbose_name=_('Classes to which these notes belong'),
        help_text=_('Classes to which these notes belong')
    )
    notes_file = models.FileField(
        upload_to='notes_files/',
        blank=True,
        null=True,
        verbose_name=_('Notes File'),
        help_text=_('The actual notes document file (PDF, Word, etc.)'),
        validators=[FileExtensionValidator(allowed_extensions=[ 'pdf', 'docx','txt','doc']),validate_file_size]
    )
    notes_link = models.URLField(
        blank=True,
        null=True,
        verbose_name=_('Notes URL'),
        help_text=_('Provide a link if the notes are available online')
    )
    pretext = models.TextField(
        blank=True,
        verbose_name=_('pretext'),
        help_text=_('A brief pretext on what is covered and what is not')
    )
    book_used_notes = models.ForeignKey(
        'Book',
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='notes',
        verbose_name=_('book_used_notes'),
        help_text=_('Book used to create the notes, specify if it is in the library')
    )
    textbook = models.TextField(
        blank=True,
        verbose_name=_('Textbook referred'),
        help_text=_('Textbook from which notes are created')
    )
    notes_saved_by_users = models.ManyToManyField(
        'User', 
        related_name='notes_saved_by_users', 
        blank=True,
        verbose_name=_('Saved by Users'),
        help_text=_('Users who saved this notes'),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))



    class Meta:
        verbose_name = _('Notes')
        verbose_name_plural = _('Notes')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} - {self.created_by} "
    
    def clean(self):
        if not self.notes_file and not self.notes_link:
            raise ValidationError(_("Either upload a file or provide a link."))

        if self.notes_file and self.notes_link:
            raise ValidationError(_("You can't have both a file and a URL for the notes. Choose one."))

    def save(self, *args, **kwargs):
        if not self.notes_id:
            created_timestamp = now().strftime('%f-%S-%M-%H-%d-%m-%Y')  
            self.notes_id = f"N_{self.created_by.username}-{created_timestamp}"

        if not self.access_code:
            while True:
                self.access_code = generate_access_code('N')
                self.full_clean()
                try:
                    super().save(*args, **kwargs)
                    break  # success
                except IntegrityError:
                    continue  # regenerate access_code and try again
        else:
            self.full_clean()
            super().save(*args, **kwargs)

    
    def delete(self, *args, **kwargs):
        """Override delete to ensure file attachments are also removed."""
        if self.notes_file:
            self.notes_file.delete(save=False)
        super().delete(*args, **kwargs)



class Announcement(models.Model):
    PRIORITY_CHOICES = [
        ('high', _('High')),
        ('normal', _('Normal')),
        ('low', _('Low')),
    ]


    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    ]

    announcement_id = models.CharField(
        max_length=255,
        primary_key=True,
        editable=False,
        verbose_name=_('Announcement ID'),
        help_text=_('A unique identifier for the announcement starting with A')
    )
    
    # Related to the class
    Class = models.ForeignKey(
        'Class',
        on_delete=models.CASCADE,
        related_name='announcements',
        verbose_name=_('Class'),
        help_text=_('The class for which this announcement is made'),
    )
    # Announcement details
    title = models.CharField(
        max_length=128,
        verbose_name=_('Announcement Title'),
        help_text=_('Title of the announcement')
    )
    content = models.TextField(
        verbose_name=_('Announcement Content'),
        help_text=_('The detailed content of the announcement')
    )
    
    # Created by teacher
    created_by = models.ForeignKey(
        'User',  
        on_delete=models.CASCADE,
        related_name='created_announcements',
        verbose_name=_('Created By'),
        help_text=_('Teacher who created the announcement')
    )
    
    # Dates and time handling
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    expire_at = models.DateTimeField(
        verbose_name=_('Expires At'),
        help_text=_('Date and time when the announcement will expire')
    )
    
    # Visibility controls
    visibility = models.CharField(
        max_length=12,
        choices=VISIBILITY_CHOICES,
        default='student',
        verbose_name=_('Visibility'),
        help_text=_('Who can view this announcement?')
    )
    
    # Priority of the announcement
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='normal',
        verbose_name=_('Priority'),
        help_text=_('Priority level of the announcement')
    )
    
    # Attachment field to upload files like PDFs, images, etc.
    attachment = models.FileField(
        upload_to='announcement_attachments/',
        blank=True, null=True,
        verbose_name=_('Attachment'),
        help_text=_('Optional file attachment for the announcement'),
        validators=[FileExtensionValidator(allowed_extensions=[ 'pdf', 'docx','txt','doc']),validate_file_size]
    )

    # A boolean to indicate whether the announcement is pinned at the top
    is_pinned = models.BooleanField(
        default=False,
        verbose_name=_('Pinned'),
        help_text=_('If the announcement should be pinned at the top of the list'),
        db_index=True
    )

    #will be made spearate above the announcement div for piinned ., if no pinned the recent one will be selected

    class Meta:
        verbose_name = _('Announcement')
        verbose_name_plural = _('Announcements')
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        # Get the created_at field and format it
        formatted_date = self.created_at.strftime('%d-%m-%y %H:%M')  # dd-mm-yy HH:MM
        return f"{formatted_date}- {self.Class.name} ({self.get_priority_display()})"
    
    
    def is_expired(self):
        """Checks if the announcement is expired."""
        return timezone.now() > self.expire_at
        

    def save(self, *args, **kwargs):
        # Automatically set the announcement_id before saving the instance
        if not self.announcement_id:
            # Generate the notes_id as a combination of "N", username and creation timestamp
            created_timestamp = now().strftime('%f-%S-%M-%H-%d-%m-%Y')  # Format the timestamp part
            # Generate the unique announcement_id: 'C<username>-<increment>'
            
            self.announcement_id = f"AN_{self.created_by.username}-{created_timestamp}-{self.Class.class_id}"
        super().save(*args, **kwargs)
    
    def delete(self, *args, **kwargs):
        """Override delete to ensure file attachments are also removed."""
        if self.attachment:
            self.attachment.delete(save=False)
        super().delete(*args, **kwargs)



class Assignment(models.Model):
    assignment_id = models.CharField(
        max_length=255,
        primary_key=True,
        editable=False,
        verbose_name=_('Assignment ID'),
    )
    title = models.CharField(max_length=255, verbose_name=_('Title'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    created_by = models.ForeignKey(
        'User', on_delete=models.CASCADE, related_name='assignments', verbose_name=_('Created By')
    )
    class_assigned = models.ForeignKey(
        'Class', on_delete=models.CASCADE, related_name='assignments', verbose_name=_('Class')
    )
    due_date = models.DateTimeField(verbose_name=_('Due Date'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    file = models.FileField(
        upload_to='assignment_files/', 
        blank=True, 
        null=True, 
        verbose_name=_('File Attachment'), 
        validators=[FileExtensionValidator(allowed_extensions=[ 'pdf', 'docx','txt','doc']),validate_file_size]
    )

    def __str__(self):
        return f"{self.title} ({self.class_assigned.name})"
    
    
    def save(self, *args, **kwargs):
        """
        Override save method to generate assignment_id in the format 'AS_<created_by>-<class_id>-<timestamp>'.
        """
        if not self.assignment_id:
            timestamp = now().strftime('%f-%S-%M-%H-%d-%m-%Y')  # Unique timestamp
            self.assignment_id = f"AS_{self.created_by.username}-{self.class_assigned.class_id}-{timestamp}"

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Override delete to ensure file are also removed."""
        if self.file:
            self.file.delete(save=False)
        super().delete(*args, **kwargs)



class AssignmentSubmission(models.Model):
    assignment_submission_id = models.CharField(
        primary_key=True,
        editable=False,
        max_length=255,
        verbose_name=_('Assignment Submission ID'),
    )
    assignment = models.ForeignKey(
        'Assignment', on_delete=models.CASCADE, related_name='submissions', verbose_name=_('Assignment')
    )
    submitted_by = models.ForeignKey(
        'User', on_delete=models.CASCADE, related_name='submissions', verbose_name=_('Submitted By')
    )
    submitted_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Submitted At'))
    file = models.FileField(
        upload_to='assignment_submissions/', blank=True, null=True, verbose_name=_('File Submission'),
        validators= [FileExtensionValidator(allowed_extensions=[ 'pdf', 'docx','txt','doc']),validate_file_size]
    )
    text_response = models.TextField(blank=True,  verbose_name=_('Text Response'))
    marks = models.DecimalField(
        max_digits=5, decimal_places=2, default=0, verbose_name=_('Marks')
    )
    remarks = models.TextField(blank=True, verbose_name=_('Remarks'))
    
    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['assignment', 'submitted_by'], name='unique_submission_per_user')
        ]
        ordering = ['submitted_at']  

    '''def clean(self):
        """
        Validate that the user has not already submitted the assignment.
        """
        if AssignmentSubmission.objects.filter(assignment=self.assignment, submitted_by=self.submitted_by).exists():
            raise ValidationError("User has already submitted this assignment!")'''
    
    def save(self, *args, **kwargs):
        """
        Override save method to generate assignment_submission_id in the format 'ASS_<submitted_by>-<assignment_id>-<timestamp>'.
        """

        if not self.assignment_submission_id:
            timestamp = now().strftime('%f-%S-%M-%H-%d-%m-%Y')  # Unique timestamp
            self.assignment_submission_id = f"ASS_{self.submitted_by.username}-{self.assignment.assignment_id}-{timestamp}"

        '''self.full_clean()  # Ensure validation is applied'''
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.submitted_by.username} by {self.assignment}"
    
    def delete(self, *args, **kwargs):
        """Override delete to ensure file  are also removed."""
        if self.file:
            self.file.delete(save=False)
        super().delete(*args, **kwargs)



class Book(models.Model):
    ACCESS_TYPE_CHOICES = [
        ('public', 'Public'),
        ('private', 'Private'),
    ]

    book_id = models.CharField(
        max_length=255,
        primary_key=True,
        editable=False,
        verbose_name=_('Book ID'),
        help_text=_('A unique identifier for the Book starting with B')
    )
    name = models.CharField(max_length=255, help_text="Title of the book", db_index=True)
    author = models.CharField(max_length=255, help_text="Author of the book", db_index=True)
    edition = models.PositiveIntegerField(help_text="Edition of the book in words", blank=True, validators=[MinValueValidator(0)])
    publisher = models.CharField(max_length=255, blank=True, help_text="Publisher of the book")
    isbn = models.CharField(max_length=17, unique=True, help_text="ISBN number",db_index=True)
    genre = models.CharField(max_length=100, blank=True,  help_text="Genre of the book")
    language = models.CharField(max_length=50, help_text="Language of the book")
    num_pages = models.PositiveIntegerField(blank=True, null=True, help_text="Number of pages")
    cover_image = models.ImageField(
        null=True,blank=True,
        upload_to='book_covers/', help_text="Cover image of the book",
        validators=[
            FileExtensionValidator(allowed_extensions=['png', 'jpeg','jpg']),validate_file_size]   
    )
    file = models.FileField(
        upload_to='book_files/',
        help_text="Upload the digital version of the book (PDF, ePub, etc.)",
        validators= [FileExtensionValidator(allowed_extensions=[ 'pdf', 'docx','txt','doc','epub']),
                    partial(validate_file_size, max_size_mb=100)]
    )
    created_by = models.ForeignKey(
        'User',  # Refers to your custom User model
        on_delete=models.CASCADE,
        related_name='books',
        verbose_name=_('Created By'),
    )
    access_type = models.CharField(
        max_length=7,
        choices=ACCESS_TYPE_CHOICES,
        default='PUBLIC',
        help_text="Defines whether the book is public or private"
    )
    access_code = models.CharField(
        max_length=7,
        blank=True,
        unique=True,
        help_text="Access code for private books."
    )
    book_saved_by_users = models.ManyToManyField(
        'User', 
        related_name='book_saved_by_users', 
        blank=True,
        verbose_name=_('Saved by users'),
        help_text=_('Users who saved this book'),
    )
    created_at = models.DateTimeField(auto_now_add=True, help_text="Timestamp when the book was added")
    updated_at = models.DateTimeField(auto_now=True, help_text="Timestamp when the book details were last updated")

    def __str__(self):
        return f"{self.name} ({self.access_type})"
    


    def save(self, *args, **kwargs):
        """
        Override save method to generate quiz_id in the format 'K<user_id>-<increment>'.
        """
        if not self.book_id:
            # Generate the notes_id as a combination of "N", username and creation timestamp
            created_timestamp = now().strftime('%f-%S-%M-%H-%d-%m-%Y')  # Format the timestamp part
            self.book_id = f"B_{self.created_by.username}-{created_timestamp}"
        
        if not self.access_code:
            while True:
                self.access_code = generate_access_code('B')
                try:
                    super().save(*args, **kwargs)
                    break
                except IntegrityError:
                    continue  # regenerate and try again
        else:
            super().save(*args, **kwargs)


    
    def delete(self, *args, **kwargs):
        """Override delete to ensure file attachments are also removed."""
        if self.file:
            self.file.delete(save=False)
        if self.cover_image:
            self.cover_image.delete(save=False)
        super().delete(*args, **kwargs)

    '''   
    later we can implement that private books will be accessed 
    by a code generated by sytem that will be unique for each user
    and can only be redeemned once after payment
    '''