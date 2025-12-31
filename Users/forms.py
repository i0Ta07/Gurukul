#from django.forms import ModelForm

from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import *
from django.utils.safestring import mark_safe
from django.db.models import Q

from django.forms import ModelForm
from .models import *



from django.contrib.auth.forms import AuthenticationForm


from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from datetime import date

'''
When we use modelForms Validators are called automatically with form.is_valid() 
When we create an object in the view and save it validators are not called 
We have to explicitely call self.full_clean()

'''


class CustomUserCreationForm(UserCreationForm):
    # Additional fields
    title = forms.ChoiceField(choices=User.TITLE_TYPE_CHOICES, required=True)
    phone_number = forms.CharField(max_length=15, required=True, help_text='phone number')
    date_of_birth = forms.DateField(widget=forms.TextInput(attrs={'type': 'date'}), required=True, help_text='Optional')
    user_type = forms.ChoiceField(choices=User.USER_TYPE_CHOICES, initial='student', required=True)
    friends = forms.ModelMultipleChoiceField(
        queryset=User.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    profile_photo = forms.ImageField(required=False, help_text="Optional: Upload a profile photo")


    class Meta:
        model = User
        fields = ('username', 'password1', 'password2', 'title', 'phone_number', 'date_of_birth', 'user_type','friends','profile_photo')
        # fields is what we want to show in the form 

    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')
        if phone_number and len(phone_number) != 10:
            raise forms.ValidationError("Phone number must be 10 digits.")
        return phone_number 


# UserCreationForm handles password hashing
class RegisterForm(UserCreationForm):
    TITLE_CHOICES = [
        ('Mr.','Mr.'),
        ('Mrs.','Mrs.'),
        ('Miss.','Miss.'),
        ('Ms.','Ms.'),
        ('Dr.','Dr.'),
    ]
    
    USER_TYPE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
    ]
    
    title = forms.ChoiceField(
        choices=TITLE_CHOICES,
        label=_('Title'),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    phone_number = forms.CharField(
        max_length=15,
        label=_('Phone Number'),
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    user_type = forms.ChoiceField(
        choices=USER_TYPE_CHOICES,
        label=_('User Type'),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
    )
    
    first_name = forms.CharField(
        max_length=30,
        required=True,
        label=_('First Name'),
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    last_name = forms.CharField(
        max_length=30,
        required=True,
        label=_('Last Name'),
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )
    email = forms.EmailField(
        max_length=254,
        required=True,
        label=_('Email Address'),
        widget=forms.EmailInput(attrs={'class': 'form-control'}),
    )

    # Adding date of birth
    date_of_birth = forms.DateField(
        required=True,
        label=_('Date of Birth'),
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
    )
    
    # Meta class to define model and fields
    class Meta:
        model = User
        fields = [
            'title', 'first_name', 'last_name', 'username', 'email', 'phone_number', 
            'user_type', 'date_of_birth', 'password1', 'password2',
        ]
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data['phone_number']
        if len(phone_number) != 10:
            raise ValidationError(_('Phone number must be at least 10 digits.'))
        return phone_number
    
    
    def clean_date_of_birth(self):
        dob = self.cleaned_data['date_of_birth']
        today = date.today()
        age = today.year - dob.year - ((today.month, today.day) < (dob.month, dob.day))

        if age < 13:
            raise ValidationError(_('You must be at least 13 years old to register.'))
        return dob
    
    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exists():
            raise ValidationError(_('Email already registered'))
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.phone_number = self.cleaned_data['phone_number']
        user.user_type = self.cleaned_data['user_type']
        user.title = self.cleaned_data['title']
        user.date_of_birth = self.cleaned_data['date_of_birth']

        '''
        # Set extra fields not handled by UserCreationForm
        for field in ['first_name', 'last_name', 'email', 'phone_number', 'user_type', 'title', 'date_of_birth']:
            setattr(user, field, self.cleaned_data[field])

        '''
    

        user.is_active = True  # Default to True
        user.is_staff = False
        user.is_superuser = False
    
        if commit:
            user.save()
        return user
    
class LoginForm(AuthenticationForm):
    """
    This form is used for user authentication (login).
    It inherits from Django's built-in AuthenticationForm for simplicity.
    """
    username = forms.CharField(
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter username'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter password'})
    )

    
    # Optionally, you can add custom validation methods here if needed.

class SingleQuestionForm(forms.Form):
    """
    Form to handle quiz questions, allowing users to respond or skip.
    """
    #kwargs is a dictionary
    def __init__(self, *args, **kwargs):
        quiz = kwargs.pop('quiz')
        user = kwargs.pop('user')
        current_question = kwargs.pop('current_question')
        super().__init__(*args, **kwargs)

        self.quiz = quiz
        self.user = user
        self.current_question = current_question

        # Determine field type based on question type
        # Using mark_safe will render the HTML within the label field correctly.

        question_label = f"<span class='question-text'>{self.current_question.question_text}</span>"

        # If the question has an image, append it to the label
        if self.current_question.question_image:
            question_label += f"<br><img src='{self.current_question.question_image.url}' class='question-image' alt='Question Image'>"

        field_kwargs = {
            # "label": mark_safe(f"<span class='fs-2'>{self.current_question.question_text}</span>"),
             "label":  mark_safe(question_label), 
            "required": False,  # Allows skipping the question
        }

        if self.current_question.question_type == 'mcq':
            field_kwargs["choices"] = [(opt, opt) for opt in self.current_question.options]
            field_kwargs["widget"] = forms.RadioSelect
            self.fields["answer"] = forms.ChoiceField(**field_kwargs)

        elif self.current_question.question_type == 'true_false':
            field_kwargs["choices"] = [("True", "True"), ("False", "False")]
            field_kwargs["widget"] = forms.RadioSelect
            self.fields["answer"] = forms.ChoiceField(**field_kwargs)

        elif self.current_question.question_type == 'text':
            field_kwargs["widget"] = forms.Textarea(attrs={"rows": 3, "cols": 50, "class": "dark-charfield"})
            self.fields["answer"] = forms.CharField(**field_kwargs)


        # Pre-fill the previously saved answer
        previous_answer = Answer.objects.filter(answered_by=user, question=self.current_question).first()

        if previous_answer:
            if self.current_question.question_type == 'mcq' or self.current_question.question_type == 'true_false':
                self.initial["answer"] = previous_answer.selected_option
            elif self.current_question.question_type == 'text':
                self.initial["answer"] = previous_answer.text_answer



class create_announcement_form(ModelForm):
    class Meta:
        model = Announcement
        fields = ['Class', 'title', 'content', 'visibility', 'priority', 'attachment', 'expire_at', 'is_pinned']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter title'}),
            'content': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Enter content'}),
            'visibility': forms.Select(attrs={'class': 'form-select'}),
            'priority': forms.Select(attrs={'class': 'form-select'}),
            'expire_at': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'attachment': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'is_pinned': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

   
    def __init__(self, *args, **kwargs):
        class_instance = kwargs.pop('class_instance', None)
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        

        '''
        Initial vs Bound Data:
        Setting self.initial['Class'] in the form's __init__ method only affects the initial display of the field; it doesn't bind the value when no data is submitted.
        only affects what is rendered in the form. If that field isn’t included in the submitted POST data—such as when it's hidden—it won’t automatically bind to the model instance during form.save(commit=False).
        ou need to explicitly assign it to the model instance in the view or make changes in the save.
        '''
        if class_instance:
            self.fields['Class'].widget = forms.HiddenInput()
            self.initial['Class'] = class_instance
        else:
            self.fields['Class'].widget = forms.Select(attrs={'class': 'form-select'})  # Dropdown styling


        # Set queryset dynamically
        if user:
            if user.user_type == 'teacher':
                self.fields['Class'].queryset = Class.objects.filter(Q(teachers=user) | Q(created_by=user)).distinct()
            elif user.user_type == 'student':
                self.fields['Class'].queryset = Class.objects.filter(students=user)

            self.user = user  # Store user for later use

        

    def save(self, commit=True):
        '''
        Hanling the expicit saving of the class and user here in the save method.
        '''
        announcement = super().save(commit=False)
        
        
        class_instance = self.cleaned_data.get('Class', None)  # Use cleaned_data, not initial
        if class_instance:
            announcement.Class = class_instance

        if self.user:
            announcement.created_by = self.user

        if commit:
            announcement.save()
        
        return announcement

class studentAssignmentSubmissionForm(ModelForm):
    class Meta:
        model = AssignmentSubmission
        fields = ['file', 'text_response', 'remarks']
        widgets = {
            'file': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'text_response': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter your response here...'
            }),
            'remarks': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Remarks (optional)...'
            }),
        }

    

    def clean(self):
        cleaned_data = super().clean()
        
        file = cleaned_data.get('file')
        text_response = cleaned_data.get('text_response')

        if not file and not text_response:
            raise ValidationError("You must provide at least one of: File or Text Response.")

        return cleaned_data
    

