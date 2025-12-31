from django.urls  import path
from  .views import *


urlpatterns = [
    path('home/',chat_home,name='chat_home'), # home page of the chat app i.e public chat
    path('chat/<str:username>/',get_or_create_chatroom, name='start_chat'), #when this is clicked we check with the function that if the chatroom already exists if not create then redirect user to that chatroom
    path('room/<str:chatroom_name>/',chat_home, name="chatroom"),
    path('create/new_groupchat/',create_groupchat, name="new_groupchat"),
    path('edit/<str:chatroom_name>',edit_chatroom,name="edit_chatroom"),
    path('delete/<str:chatroom_name>',delete_chatroom,name="delete_chatroom"),
    path('leave/<str:chatroom_name>',leave_chatroom,name="leave_chatroom"),
    
]