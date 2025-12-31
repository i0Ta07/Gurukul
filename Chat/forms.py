from django.forms import ModelForm
from django import forms
from .models import *

class chat_message_create_form(ModelForm):
    class Meta:
        model = GroupMessage
        fields = ['body']
        labels = {
            'body': '',  # Hide the label
        }
        # We cam add the class here only
        widgets = {
    'body': forms.TextInput(attrs={
        'placeholder': 'Add message ...',
        'class': 'form-control py-3',
        'maxlength': '300',
        'autofocus': True
    }),
}
        
class new_group_form(ModelForm):
    class Meta:
        model = ChatGroup
        fields = ['groupchat_name']
        widgets = {
            'groupchat_name': forms.TextInput(attrs={
                'placeholder':'Add name ...',
                'class':'form-control py-3 w-50 ',
                'maxlength' : '128',
                'autofocus':True
            }),
        }


class edit_chatroom_form(ModelForm):
    class Meta:
        model= ChatGroup
        fields = ['groupchat_name']
        widgets = {
            'groupchat_name':forms.TextInput(attrs={
                'class':'form-control  w-50 fw-bolder ',
                'maxlength' : '300'
            }),
        }
