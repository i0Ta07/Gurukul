from django.contrib import admin
from .models import *
# Register your models here.

from .forms import CustomUserCreationForm
from django.contrib.auth.admin import UserAdmin

#from .models import User,Quiz,Question,Class,Result,Notes



class CustomUserAdmin(UserAdmin):
    model = User
    add_form = CustomUserCreationForm


    #when user is modified
    # Define fieldsets for the User model
    fieldsets = (
        *UserAdmin.fieldsets,  # Include the default fields for the User model
        ('Personal Information', {
            'fields': (
                'title',  # Mr, Mrs, etc.
                'phone_number',  # Phone number
                'date_of_birth',  # Date of birth
                'profile_photo',

            ),
        }),
        ('Account Information', {
            'fields': (
                'user_type',  # Type of user (Teacher, Student)
            ),
        }),
    )

    #when user is created
    #default field sets
    # Define add_fieldsets for the User creation form when created form admin site
    add_fieldsets = (
        (None, {
            'fields': (
                'username',  # Username
                'password1',  # Password
                'password2',  # Password confirmation
                'user_type', # Type of user (Teacher, Student)
            ),
        }),
        ('Personal Information', {
            'fields': (
                'title',  # Title (Mr, Mrs, etc.)
                'first_name',
                'last_name',
                'email',
                'phone_number',  # Phone number
                'date_of_birth',  # Date of birth
                
            ),
        }),
        ('Permissions', {
            'fields': (
                'is_active',
                'is_superuser',
                'is_staff',
                'user_permissions',
                'groups',
            ),
        }),
    )
    #to show in admin panel the customUseradmin createion form
   
    filter_horizontal = ('user_permissions','groups') #two boxes in admin panel for giving permssions
    # Make the form appear correctly
    list_display = ('__str__','date_of_birth')
    search_fields = ('username', 'title', 'phone_number')
    ordering = ('username',)


admin.site.register(User,CustomUserAdmin)
admin.site.register(Quiz)
admin.site.register(Question)
admin.site.register(Class)
admin.site.register(Notes)
admin.site.register(Answer)
admin.site.register(Announcement)
admin.site.register(Book)
admin.site.register(Attempt)
admin.site.register(Assignment)
admin.site.register(AssignmentSubmission)
admin.site.register(Friend)


