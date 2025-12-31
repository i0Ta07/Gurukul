from django.shortcuts import render,redirect,get_object_or_404
from django.http import  HttpResponseBadRequest, HttpResponse
from django.contrib.auth import login,authenticate,logout
from django.contrib.auth.forms import UserCreationForm
from Users.filters import *
from django.template.loader import render_to_string





from django.http import JsonResponse
import numpy as np
import random
from django.contrib import messages
from django.db.models import Count,Q



from django.contrib.auth.decorators import login_required

from .forms import *

from .models import *


# Create your views here.
# we create views that we want to show in the website like we
# Create a view that distinguishes between teachers and students and retrieves quizzes accordingly.


# All the views inside the Users app will be stored here


# we create the forms in forms.py and instantiate that form
# here which make that form available in the html file 
# for example the Registerform() is intantiated in  registerPage via register.html


'''
How django looks for templates
-Users
--templates
---Users
----dashboard.html
----student_class.html
----student.html
----teacher.html

'''




def registerPage(request):
    form = RegisterForm()
    #logged in user cannot go to login page redirect to user page
    if request.user.is_authenticated:
        return redirect('user_home')
    else: 
        if request.method == 'POST':
            form = RegisterForm(request.POST)
            if form.is_valid():
                form.save()
                user = form.cleaned_data.get('username')
                messages.success(request,'Account for ' + user + ' has been created successfully')
                return redirect('login')

        # this is if the form is not valid rereder the form with errors 
        context = {'form': form}
        #  context is typically a Python dictionary.The keys are the variable
        #  names used in the template, and the values are the data they represent.
        # render takes 3 arguments request, html page to render and 
        # context : dictionary containing data to render the template.
        return render(request,'Users/base-forms/register.html',context)

def loginPage(request):
    if request.user.is_authenticated:
        return redirect('user_home')
    else:
        if request.method == 'POST':
            username = request.POST.get('username')
            password = request.POST.get('password')
            
            user = authenticate(request, username=username, password=password)
            
            if user is not None:
                # If user is valid, log them in
                login(request, user)
                return redirect('user_home')
            else:
                messages.info(request,'Username or password is incorrect')
        
        context = {}
        return render(request,'Users/base-forms/login.html',context)

def logoutUser(request):
    logout(request)
    return redirect('login')

def home(request):
    return render(request, 'Users/home.html')
 


@login_required(login_url='login')
def user_home(request):
    user = request.user
    context = {}
    
    if user.user_type == 'student':
        classes = (Class.objects.filter(students=user).annotate(student_count=Count('students')
                ).select_related('created_by').only(
                    'class_id', 'name', 'current_topic', 'next_class_date',
                    'created_by__title', 'created_by__first_name', 'created_by__last_name'
                )[:5])
        quizzes = Quiz.objects.filter(
            Q(assigned_to=user) | Q(assigned_classes__students=user)
        ).only('quiz_id', 'name', 'created_by').distinct()[:5]
        announcements = Announcement.objects.filter(
            visibility__in=['student', 'public'],
            Class__students=user,expire_at__gt=timezone.now()
        )[:5]

    elif user.user_type == 'teacher':
        classes = (Class.objects.filter(Q(teachers=user) | Q(created_by=user))
                .annotate(student_count=Count('students'))
                .only(
                    'class_id', 'name', 'current_topic', 'next_class_date',
                    'created_by__title', 'created_by__first_name', 'created_by__last_name'
                )
                .distinct()[:5])
        quizzes = Quiz.objects.filter(Q(created_by=user) | Q(assigned_to=user)).distinct().only('quiz_id', 'name', 'created_by')[:5]
        announcements = Announcement.objects.filter(
            visibility__in=['teacher', 'public'],
            Class__teachers=user,expire_at__gt=timezone.now()
        )[:5]


    context.update({'classes': classes, 'quizzes': quizzes, 'announcements': announcements})
    return render(request, 'Users/users/user_home.html', context)

@login_required(login_url='login')
def profile(request, username=None):
    
    return render(request, 'Users/users/profile.html', {'username': username})

def user_friends_list(request):
    user= request.user
    pending_req = Friend.objects.filter(to_user= user, status = 'pending')
    friends1 = Friend.objects.filter(from_user=user, status='accepted').values_list('to_user', flat=True)
    friends2 = Friend.objects.filter(to_user=user, status='accepted').values_list('from_user', flat=True)
    # Here if the user is in 'from' or 'to'  it is considered a friendship no need to make a second object 
    friends = User.objects.filter(Q(id__in=friends1) | Q(id__in=friends2))
        
    if request.method == 'POST':
        action = request.POST.get('action')  # "accept" or "reject"
        req_id = request.POST.get('req_id')
        req_obj = Friend.objects.filter(id=req_id).first()

        if req_obj:
            if action == 'accept':
                req_obj.status = 'accepted'
                req_obj.save(update_fields=['status'])
            elif action == 'reject':
                req_obj.delete()

        return redirect('user_friends_list')

    context = {
        'pending_req': pending_req,
        'friends': friends,
    }
    
    return render(request,'Users/users/user_friends_list.html',context)






@login_required(login_url='login')
def announcement_list(request):
    """
    Displays announcements based on their visibility settings and the user's class association.
    """
    user = request.user

    if user.user_type == 'student':
        announcements = Announcement.objects.filter(
            visibility__in=['student', 'public'],
            Class__students=user,expire_at__gt=timezone.now()
        )

    elif user.user_type == 'teacher':
        announcements = Announcement.objects.filter(
            visibility__in=['teacher', 'public'],
            Class__teachers=user,expire_at__gt=timezone.now()
        )

    context = {'announcements': announcements}
    return render(request, 'Users/announcements/announcement_list.html', context)

@login_required(login_url='login')
def announcement_class_list(request, class_id):
    """
    Displays announcements based on their visibility settings and the user's class association.
    """
    user = request.user
    selected_class = get_object_or_404(Class, class_id=class_id)

    if user.user_type == 'student':
        announcements = Announcement.objects.filter(
            visibility__in=['student', 'public'],
            Class=selected_class,expire_at__gt=timezone.now()
        )

    elif user.user_type == 'teacher':
        announcements = Announcement.objects.filter(
            visibility__in=['teacher', 'public'],
            Class=selected_class,expire_at__gt=timezone.now()
        )

    context = {'announcements': announcements}
    return render(request, 'Users/announcements/announcement_class_list.html', context)








@login_required(login_url='login')
def class_list(request):
    user = request.user

    if user.user_type == 'teacher':
        # Get classes where the user is either a teacher or the creator
        classes = (Class.objects.filter(Q(teachers=user) | Q(created_by=user))
                   .annotate(student_count=Count('students'))
                   .select_related('created_by')
                   .only(
                       'class_id', 'name', 'current_topic', 'next_class_date',
                       'created_by__title', 'created_by__first_name', 'created_by__last_name'
                   )
                   .distinct())

    elif user.user_type == 'student':
        classes = Class.objects.filter(students=user)

    context = {'classes': classes}
    return render(request, 'Users/classes/class_list.html', context)


@login_required(login_url='login')
def class_home(request,class_id):
    user = request.user
    selected_class = get_object_or_404(Class, class_id=class_id)
    assignments = selected_class.assignments.all()[:10]
    books = selected_class.book_used_class.all()
    notes_of_class = selected_class.notes.all()[:10]
    
    if user.user_type == "student":
        announcement_of_class = selected_class.announcements.filter(visibility__in=["public", "student"],expire_at__gt=timezone.now())[:7]
    if user.user_type == "teacher":
        announcement_of_class = selected_class.announcements.filter(visibility__in=["public", "teacher"],expire_at__gt=timezone.now())[:7]
    
    context = {
            'class' : selected_class,
            'announcements': announcement_of_class,
            'notes': notes_of_class,
            'books':books,
            'assignments':assignments
        }
    return render(request, 'Users/classes/class_home.html', context)

    
@login_required
def leave_class(request, class_id):
    user = request.user
    selected_class = get_object_or_404(Class, class_id=class_id)
    
    if user in selected_class.students.all():
        selected_class.students.remove(user)  
        messages.success(request, "You have successfully left the class.")
    
    return redirect('user_home') 





@login_required(login_url='login')
def notes_class_list(request,class_id):
    
    selected_class = get_object_or_404(Class, class_id=class_id)
    notes_of_class = selected_class.notes.all()
    context = {'notes' : notes_of_class}
    return render(request, 'Users/notes/notes_class_list.html',context)


@login_required(login_url='login')
def notes_created_list(request):
    user = request.user
    notes = Notes.objects.filter(created_by = user)
    context = {'notes' : notes}
    return render(request, 'Users/notes/notes_created_list.html',context)


@login_required(login_url='login')
def notes_saved_list(request):
    user = request.user
    notes = Notes.objects.filter(notes_saved_by_users= user)
    context = {'notes' : notes}  
    return render(request, 'Users/notes/notes_saved_list.html',context)



@login_required(login_url='login')
def books_created_list(request):
    user  = request.user
    books = Book.objects.filter(created_by = user)
    context = {'books' : books}
    return render(request, 'Users/books/books_created_list.html',context)

@login_required(login_url='login')
def books_saved_list(request):
    user  = request.user
    books = Book.objects.filter(book_saved_by_users = user)
    context = {'books' : books}
    return render(request, 'Users/books/books_saved_list.html',context)



@login_required(login_url='login')
def quiz_class_list(request,class_id):
   
    selected_class = get_object_or_404(Class, class_id=class_id)
    quizzes_of_class = selected_class.quizzes.all()
    context = {'quizzes' : quizzes_of_class}
    return render(request, 'Users/quiz/quiz_class_list.html',context)



@login_required(login_url='login')
def quiz_saved(request):
    user= request.user
    quizzes = Quiz.objects.filter(quiz_saved_by_users= user)
    context = {'quizzes': quizzes}    
    return render(request, 'Users/quiz/quiz_saved.html',context)

@login_required(login_url='login')
def quiz_user_all_classes(request):
    user = request.user
    if user.user_type == 'teacher':
        classes = Class.objects.filter(teachers=user)
    else:
        classes = Class.objects.filter(students=user)

    quizzes = Quiz.objects.filter(assigned_classes__in=classes).only('quiz_id', 'name', 'time_limit', 'updated_at', 'end_time', 'created_by_id').distinct()
    
    
        

    context = {'quizzes': quizzes}    
    return render(request, 'Users/quiz/quiz_user_all_classes.html',context)


@login_required(login_url='login')
def quiz_created(request):
    user = request.user  
    if user.user_type == 'teacher':
        quizzes = Quiz.objects.filter(created_by=user).only(
            'quiz_id', 'name', 'time_limit', 'updated_at', 'end_time', 'created_by'
        )  # `created_by_id` is unnecessary; `created_by` already includes it.

    return render(request, 'Users/quiz/quiz_created.html', {'quizzes': quizzes})



@login_required(login_url='login')
def quiz_assigned(request):
    user= request.user
    # Quiz that are assigned and not attempted
    quizzes = Quiz.objects.filter(assigned_to = user).only('quiz_id', 'name', 'time_limit', 'updated_at', 'end_time', 'created_by_id').distinct()
    context = {'quizzes': quizzes}
    return render(request, 'Users/quiz/quiz_assigned.html',context)





@login_required(login_url='login')
def quiz_guidelines(request,quiz_id):
    quiz = get_object_or_404(Quiz, quiz_id=quiz_id)
    attempt = Attempt.objects.filter(quiz = quiz,user = request.user, completed_at__isnull = False).first()
    if attempt:
        return redirect('quiz_submission',attempt_id= attempt.attempt_id)
    else:
        '''
        update the max marks when the quiz is taken for the first time 
        if updated by the teacher then it will be updated there only
        '''
        if request.method == 'POST' and (quiz.max_marks == 0):
            max_marks = 0
            min_marks = 0

            for q in quiz.questions.only('marks', 'negative_marks'):
                max_marks += q.marks
                min_marks += q.negative_marks

            quiz.max_marks = max_marks
            quiz.min_marks = min_marks
            quiz.save(update_fields=['max_marks', 'min_marks'])
    context={'quiz':quiz}
    return render(request, 'Users/take_quiz/quiz_guidelines.html',context)


#called in start quiz
def complete_quiz(attempt,status):
    """
    Helper function to complete the quiz, mark it as finished, and evaluate the attempt.
    """
    attempt.completed_at = now()
    if status == 'manual_submit':
        attempt.completion_reason = 'manual_submit'
        attempt.duration = (attempt.completed_at - attempt.attempt_time).total_seconds()
    elif status == 'timeout':
            attempt.completion_reason = 'timeout'
            attempt.duration = attempt.quiz.time_limit.total_seconds()

    
    # Evaluate the attempt and calculate marks
    attempt.evaluate_attempt()
    
    # Save only the relevant fields for the attempt
    attempt.save(update_fields=["completed_at", "completion_reason", "duration"])

    if attempt.quiz.quiz_type == 'objective':
        attempt.quiz.update_stats(new_score=attempt.marks_scored, new_duration=attempt.duration)
        attempt.weighted_score = attempt.quiz.score_history[-1]['weighted_score']
        attempt.save(update_fields=['weighted_score'])
    
    
    if attempt.quiz.min_duration == 0 or attempt.duration < attempt.quiz.min_duration:
        attempt.quiz.min_duration = attempt.duration
        attempt.quiz.save(update_fields=['min_duration'])
    
    attempt.calculate_weighted_percentile()
        

    # Redirect to submission page
    return redirect('quiz_submission', attempt.attempt_id)


@login_required(login_url="login")
def start_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz.objects.only('quiz_id', 'time_limit'), quiz_id=quiz_id)
    attempt = Attempt.objects.filter(user=request.user, quiz=quiz).first()


    # *********** If Attempt Exists (Continue Quiz) ***********
    if attempt: # Completed qizzes should have a seperate panel 
        if attempt.completed_at:  # If already completed, redirect to results
            return redirect('quiz_submission', attempt.attempt_id)


    # *********** If No Attempt Exists (New Quiz) ***********
    else:
        print("Attempt is created and we showed the first question")
        attempt = Attempt.objects.create(
            user=request.user,
            quiz=quiz,
            attempt_time=now(),
            end_time = now() + quiz.time_limit, #Since time_limit is a duration field
            remaining_time=quiz.time_limit.total_seconds(),
            marks_scored= 0,
            current_question_index = 0 #If the user disconnets he can resume from where he left off
        )
        attempt.shuffle_questions()

    # ** Handle Form Submission Before Changing Question Index**
    if request.method == 'POST':
        confirm_submit = request.POST.get('confirm_submit')

        '''
        ONLY GREEN -> WHEN SAVE AND NEXT IS CLICKED

        if answer is there and save and next is clicked  -> green 
        if answer is not there and save and next is clicked -> red
        if answer is not there and mark for review is clicked -> yellow 
        if answer is there and mark_for_review is clicked -> yellow with red text
        if answer is not there and mark_for_review is clicked -> yellow with white text
        if answer is there and prev is clicked -> green
        if answer is not there and prev is clicked -> red
        if question was in review and prev is clicked -> yellow
        if question was in review and save and next is clicked -> green
        '''

        if confirm_submit is not None:
            attempt.finalize(status="manual_submit")
            return redirect('quiz_submission', attempt.attempt_id)


    # *********** Render the Quiz Page ***********
    context = {
        'quiz':quiz,
        'quiz_name': quiz.name,
        'total_questions': range(quiz.questions.count()),
        'time_limit_seconds': attempt.remaining_time,        
    }
    return render(request, "Users/take_quiz/start_quiz.html", context)




@login_required(login_url='login')
def confirm_quiz(request):
    quiz_id = request.POST.get("quiz_id")

    quiz = get_object_or_404(Quiz, quiz_id=quiz_id)

    context = {'quiz': quiz}
    return render(request, "Users/take_quiz/start_quiz_modal.html", context)



@login_required(login_url='login')
def quiz_submission(request, attempt_id):
    attempt = get_object_or_404(Attempt, attempt_id=attempt_id)
    quiz = attempt.quiz
    # Update attempt status only if auto-evaluation is possible and not already set
    passing_marks= None

    if quiz.quiz_type == 'objective' and attempt.status =='pending':
        passing_marks = quiz.max_marks * 0.60  # Example: 60% passing criteria
        attempt.status = 'passed' if attempt.marks_scored >= passing_marks else 'failed'
        attempt.save(update_fields=['status'])
    


    feedback_submitted = bool(attempt.feedback) and bool(attempt.rating)
    # Handle feedback form submission
    if request.method == "POST" and not feedback_submitted:
        feedback = request.POST.get("feedback", "").strip()  # Remove whitespace
        rating = int(request.POST.get("rating"))
        #return empty string "" if no feeback is given
        attempt.feedback = feedback
        attempt.rating = rating
        quiz.update_rating(rating)
        attempt.save(update_fields=['feedback','rating'])
        messages.success(request, "Thank you for your feedback!")
        return redirect('quiz_submission',attempt_id= attempt.attempt_id)
    

    context = {
        "attempt": attempt,
        "passing_marks": passing_marks,  # Only relevant if MCQ/True-False
        "feedback_submitted": feedback_submitted,
        "quiz":quiz
    }

    return render(request, 'Users/take_quiz/quiz_submission.html', context)


@login_required(login_url='login')
def quiz_review(request, attempt_id):
    attempt = get_object_or_404(Attempt, attempt_id=attempt_id)

    # Load the list of wrong or unattempted question IDs
    wrong_not_attempted_ids = attempt.wrong_notAttempted

    # Fetch the corresponding question objects
    questions = Question.objects.filter(question_id__in=wrong_not_attempted_ids).reverse()

    all_questions = attempt.quiz.questions.all()

    # Fetch the user's answers for these questions
    answers = Answer.objects.filter(attempt=attempt, question_id__in=wrong_not_attempted_ids).values('question_id', 'selected_option')

    # Convert answers into a dictionary {question_id: selected_option}
    user_answers = {answer['question_id']: answer['selected_option'] for answer in answers}

    context = {
        'attempt': attempt,
        'questions': questions,
        'user_answers': user_answers,  # Pass user-selected options to the template
        'all_questions':all_questions,
    }

    return render(request, 'Users/take_quiz/quiz_review.html', context)



@login_required(login_url='login')
def quiz_result(request, quiz_id):
    user = request.user
    quiz = get_object_or_404(Quiz, quiz_id=quiz_id)
    attempts = Attempt.objects.filter(quiz=quiz).order_by('-marks_scored')

    # Initialize context dictionary
    context = {
        'quiz': quiz,
        'attempts': attempts,
    }

    if user.user_type == 'student':
        user_attempt = Attempt.objects.filter(user=user, quiz=quiz).first()
        context['user_attempt'] = user_attempt  # Add user attempt to context

    # Filter feedbacks based on rating conditions
    high_ratings = list(Attempt.objects.filter(quiz=quiz, rating__gte=4))
    low_ratings = list(Attempt.objects.filter(quiz=quiz, rating__lt=4))

    # Randomly select up to 5 from each category
    high_ratings_sample = random.sample(high_ratings, min(5, len(high_ratings)))
    low_ratings_sample = random.sample(low_ratings, min(5, len(low_ratings)))

    # Add feedback data to context
    context.update({
        'high_ratings_feedback': high_ratings_sample,
        'low_ratings_feedback': low_ratings_sample,
    })

    return render(request, 'Users/take_quiz/quiz_result.html', context)


@login_required(login_url='login')
def fetch_quiz_data(request, quiz_id):
    """
    Fetches and processes the latest 1000 quiz attempt data for faster graph rendering.
    Uses bucket aggregation if data size is large.
    """
    try:
        quiz = Quiz.objects.get(quiz_id=quiz_id)
        data = quiz.score_history  # List of dicts [{marks_scored: X, weighted_score: Y}, ...]

        if not data:
            return JsonResponse({"status": "error", "message": "No data available"}, status=404)

        # Extract Marks and Duration
        marks_scored = [entry["marks_scored"] for entry in data]
        weighted_score = [entry["weighted_score"] for entry in data]

        # Determine bucket size
        # mean of marks_scored and weighted_score for each bucket.
        data_size = len(marks_scored)
        if data_size > 999:
            bucket_size = 40
        elif data_size > 750:
            bucket_size = 30
        elif data_size > 500:
            bucket_size = 20 
        elif data_size > 250:
            bucket_size = 10
        elif data_size > 125:
            bucket_size = 8
        elif data_size > 100:
            bucket_size = 6
        elif data_size > 75:
            bucket_size = 4
        else:               # No aggregation
            bucket_size = 2

        # Perform bucket aggregation
        if bucket_size > 1:
            marks_scored = [np.mean(marks_scored[i:i + bucket_size]) for i in range(0, data_size, bucket_size)]
            weighted_score = [np.mean(weighted_score[i:i + bucket_size]) for i in range(0, data_size, bucket_size)]
            attempts = list(range(1, len(marks_scored) + 1))
        else:
            attempts = list(range(1, data_size + 1))

        # Compute moving averages for smooth visualization
        window_size = min(int(bucket_size/2), len(marks_scored))  # Adaptive window size
        moving_avg_marks_scored = np.convolve(marks_scored, np.ones(window_size) / window_size, mode="valid").tolist()
        moving_avg_weighted_marks = np.convolve(weighted_score, np.ones(window_size) / window_size, mode="valid").tolist()

        return JsonResponse({
            "status": "success",
            "attempts": attempts,
            "marks_scored": marks_scored,
            "weighted_score": weighted_score,
            "moving_avg_marks_scored": moving_avg_marks_scored,
            "moving_avg_weighted_marks": moving_avg_weighted_marks
        })

    except Quiz.DoesNotExist:
        return JsonResponse({"status": "error", "message": "Quiz not found"}, status=404)


@login_required(login_url='login')
def check_results(request):
    user = request.user

    if user.user_type == 'teacher':
        quizzes = Quiz.objects.filter(
            Q(created_by=user) | Q(assigned_to=user)
        ).only(
            'quiz_id', 'name', 'time_limit', 'updated_at', 'end_time', 'created_by'
        ).distinct()
    else:
        # All the Quiz user has atttempted
        quizzes = Quiz.objects.filter(
            Q(attempts__user=user)  
        ).only(
            'quiz_id', 'name', 'time_limit', 'updated_at', 'end_time', 'created_by'
        ).distinct()

    return render(request, 'Users/take_quiz/check_results.html', {'quizzes': quizzes})


@login_required(login_url='login')
def quiz_attempts(request,quiz_id):
    quiz = get_object_or_404(Quiz, quiz_id=quiz_id)
    context = {
        'quiz':quiz
        }
    if quiz.quiz_type == 'objective_and_subjective':
        attempts = Attempt.objects.filter(quiz=quiz,status = 'pending').order_by('-completed_at')
        context['attempts'] = attempts
        
    return render(request, 'Users/take_quiz/quiz_attempts.html', context)


@login_required(login_url='login')
def grade_attempt(request, attempt_id):
    attempt = get_object_or_404(Attempt, attempt_id=attempt_id)

    if request.method == 'POST':
        answer_id = request.POST.get('answer_id')
        marks = request.POST.get('marks')

        if answer_id and marks is not None:
            marks = float(marks)  
            answer = get_object_or_404(Answer, answer_id=answer_id)
            answer.marks_scored = marks
            attempt.marks_scored += marks  # Ensure marks are added as float
            answer.is_reviewed = True  # Mark as reviewed
            answer.save(update_fields=['marks_scored', 'is_reviewed'])

            

            # Append question_id if marks are less than full marks
            if marks < answer.question.marks:
                attempt.wrong_notAttempted.append(answer.question.question_id)

            # Save updated wrong_notAttempted list
            attempt.save(update_fields=['marks_scored', 'wrong_notAttempted'])

    # Check if all answers are reviewed
    if not Answer.objects.filter(attempt=attempt, is_reviewed=False).exists():
        passing_marks = attempt.quiz.max_marks * 0.60  # Example: 60% passing criteria
        attempt.status = 'passed' if attempt.marks_scored >= passing_marks else 'failed'
        attempt.save(update_fields=['status'])
        # Update quiz stats and calculate percentiles
        print("Attempt = ",attempt.marks_scored,attempt.duration)
        attempt.quiz.update_stats(new_score=attempt.marks_scored, new_duration=attempt.duration)
        attempt.weighted_score = attempt.quiz.score_history[-1]['weighted_score']
        attempt.save(update_fields=['weighted_score'])
        if attempt.quiz.min_duration == 0:
            attempt.quiz.min_duration = attempt.duration
        else:
            attempt.quiz.min_duration = min(attempt.quiz.min_duration, attempt.duration)
        
        attempt.calculate_weighted_percentile()
        messages.success(request, "All answers have been evaluated successfully.")

    # Get remaining unreviewed answers
    answers = Answer.objects.filter(attempt=attempt, is_reviewed=False).select_related('question') #prftch qie

    context = {
        'attempt': attempt,
        'answers': answers
    }

    return render(request, 'Users/take_quiz/grade_attempt.html', context)



    #give the list of question for each attempt after each attpempt when all quuestions are checked change the stauts
    # to either pass or fail then we can show the result at quiz submission and analysis
    #for teacher in the quiz_results  give option in offcanvas
    # mannually append the marks into th graph
    # calculat ethe percentile here
    #after each question save show success msg





@login_required(login_url='login')
def assignment_student(request, assignment_id):
    user = request.user
    assignment = get_object_or_404(Assignment, assignment_id=assignment_id)

    # Get the user's submission if it exists
    assignment_submission = AssignmentSubmission.objects.filter(assignment=assignment, submitted_by=user).first()

    if assignment_submission:
        messages.warning(request, "You have already submitted this assignment")
        return redirect('class_home', class_id=assignment.class_assigned.class_id)
    
    form = studentAssignmentSubmissionForm(request.POST or None,request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        submission = form.save(commit=False)
        submission.assignment = assignment
        submission.submitted_by = user
        submission.submitted_at = timezone.now()
        submission.save()
        messages.success(request, 'Assignment submitted successfully!')
        return redirect('class_home', class_id = assignment.class_assigned.class_id)

    context = {
        'assignment': assignment,
        'form': form,
    }
    return render(request, 'Users/forms/assignment_student.html', context)


@login_required(login_url='login')
def assignment_teacher(request,assignment_id):
    assignment = get_object_or_404(Assignment,assignment_id = assignment_id)
    context = {'assignment' : assignment }
    return render(request, 'Users/assignment/assignment_teacher.html',context)


@login_required(login_url='login')
def assignment_user_list(request,class_id):
    selected_class= get_object_or_404(Class,class_id=class_id)
    assignments = Assignment.objects.filter(class_assigned= selected_class)
    context={'assignments':assignments}
    return render(request, 'Users/assignment/assignment_user_list.html',context)









#FORMS



'''
Class is a ForeignKey and is part of the form fields

Django automatically includes it in form.cleaned_data, so when form.save(commit=False) is called, the Class field is already set.

Because we assign initial in __init__(), Django treats it as part of the normal form processing.

created_by is NOT a Form Field

It’s not included in the fields = '__all__' definition.

Since users should not modify created_by, we don’t include it in the form fields.

Because it's missing from form.cleaned_data, Django does not automatically assign it, so we must explicitly assign it in save().

'''


@login_required(login_url='login')
def create_announcement(request, class_id = None): #default, if not given then class_id = None
    user = request.user
    class_instance = None
    

    if class_id:
        class_instance = get_object_or_404(Class, class_id=class_id)
         # Fetch all expired announcements for the specific class
        Announcement.objects.filter(Class=class_instance, expire_at__lt = timezone.now()).delete()
    else:
        # Fetch all expired announcements created by this user
        Announcement.objects.filter(created_by= user, expire_at__lt = timezone.now()).delete()

    
    form = create_announcement_form(request.POST or None, request.FILES or None, class_instance=class_instance, user=user)

    
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, "Announcement created successfully!") 
        return redirect('class_home', class_id=class_instance.class_id) if class_instance else redirect('user_home')


    context = {'form': form, 'class_instance': class_instance}
    return render(request, 'Users/forms/create_announcement.html', context)




# FILTERS

@login_required(login_url='login')
def class_join(request):
    search_access_code = request.GET.get('access_code')
    if search_access_code:
        base_queryset = Class.objects.all()
    else:
        # Else only search in Public classes
        base_queryset = Class.objects.filter(access_type='public')

    class_filter = ClassFilter(request.GET, queryset=base_queryset)
    if request.GET and any(request.GET.values()):
        classes = class_filter.qs
    else:
        classes = Class.objects.none()
    
    class_id = request.GET.get('class_id')
    if class_id:
        user = request.user
        selected_class = Class.objects.get(class_id=class_id)
        if user in selected_class.students.all():
                messages.warning(request, "You are already in this class.")
                return redirect('class_join')
        else:
            if selected_class.students.count() < selected_class.max_students:     
                selected_class.students.add(user)
                messages.success(request, "Successfully joined the class.")
                return redirect('class_home', class_id = class_id )
            else:
                messages.error(request,"Class is full")
                return redirect('class_join')
    context = {
        'form': class_filter.form,
        'classes' : classes    
    }
    
    return render(request, 'Users/filters/class_join.html',context)


def add_friend(request):
    user_filter = UserFilter(request.GET, queryset=User.objects.all())
    if request.GET and any(request.GET.values()):
        users = user_filter.qs
    else:
        users = User.objects.none()
    target_id = request.GET.get('user_id')
    target_user = User.objects.filter(id=target_id).first()
    if target_user:
        source_user= request.user
        if target_user == source_user:
            messages.error(request,"You cannot add yourself as a friend.")
            return redirect('add_friend')
        existing_obj = Friend.objects.filter(
            Q(from_user=source_user, to_user=target_user) |
            Q(from_user=target_user, to_user=source_user)
        ).first()

        if existing_obj:
            if existing_obj.status == Friend.StatusChoices.ACCEPTED:
                messages.success(request, f"You both already friends with {target_user.username}")
            elif existing_obj.from_user == target_user and existing_obj.status == Friend.StatusChoices.PENDING:
                messages.info(request, f"{target_user.username} already sent you a friend request.")
            elif existing_obj.from_user == source_user and existing_obj.status == Friend.StatusChoices.PENDING:
                messages.info(request, "Friend request already sent by you.")
            return redirect('add_friend')
        else:
            Friend.objects.create(
                from_user=source_user,
                to_user=target_user,
            )
            messages.success(request, f"Friend request sent to {target_user.username}")
            return redirect('user_home')

    context = {
        'form': user_filter.form,
        'users' : users    
    }

    return render(request,'Users/filters/add_friend.html',context)

def search_quiz(request):
    search_access_code = request.GET.get('access_code')
    if search_access_code:
        base_queryset = Quiz.objects.all()
    else:
        # Else only search in Public quizzes
        base_queryset = Quiz.objects.filter(access_type='public')


    quiz_filter = QuizFiltter(request.GET, queryset=base_queryset)
    if request.GET and any(request.GET.values()):
        quizzes = quiz_filter.qs
    else:
        quizzes = Quiz.objects.none()

    quiz_id = request.GET.get('quiz_id')
    quiz = Quiz.objects.filter(quiz_id=quiz_id).first()
    if quiz:
        user = request.user
        if user not in quiz.quiz_saved_by_users.all():
            quiz.quiz_saved_by_users.add(user)
            messages.success(request, "Quiz saved")
        else:
            messages.error(request, "You already have this quiz saved.")
        return redirect('quiz_saved')

    context = {
        'form': quiz_filter.form,
        'quizzes': quizzes    
    }
    return render(request, 'Users/filters/search_quiz.html', context)

def search_resources(request):
    # Handle Books
    book_access_code = request.GET.get('book_access_code')
    if book_access_code:
        books_queryset = Book.objects.all()
    else:
        books_queryset = Book.objects.filter(access_type='public')

    books_filter = BooksFilter(request.GET, queryset=books_queryset)
    books_results = Book.objects.none()

    # Handle Notes
    notes_access_code = request.GET.get('notes_access_code')
    if notes_access_code:
        notes_queryset = Notes.objects.all()
    else:
        notes_queryset = Notes.objects.filter(access_type='public')

    notes_filter = NotesFilter(request.GET, queryset=notes_queryset)
    notes_results = Notes.objects.none()

    # Get form type
    form_type = request.GET.get('type')
    if form_type == 'notes':
        notes_results = notes_filter.qs
    elif form_type == 'book':
        books_results = books_filter.qs

    # Saving Notes
    notes_id = request.GET.get('notes_id')
    if notes_id:
        notes = Notes.objects.filter(notes_id=notes_id).first()
        if notes:
            user = request.user
            if user not in notes.notes_saved_by_users.all():
                notes.notes_saved_by_users.add(user)
                messages.success(request, "Notes saved")
            else:
                messages.error(request, "You already have this notes saved.")
            return redirect('notes_saved_list')

    # Saving Books
    book_id = request.GET.get('book_id')
    if book_id:
        book = Book.objects.filter(book_id=book_id).first()
        if book:
            user = request.user
            if user not in book.book_saved_by_users.all():
                book.book_saved_by_users.add(user)
                messages.success(request, "Book saved")
            else:
                messages.error(request, "You already have this book saved.")
            return redirect('books_saved_list')

    context = {
        'notes_form': notes_filter.form,
        'books_form': books_filter.form,
        'notes': notes_results,
        'books': books_results,
    }
    return render(request, 'Users/filters/search_resources.html', context)














