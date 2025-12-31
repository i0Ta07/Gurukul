from django.urls import path
from Chat.consumers import *
from Users.consumers import *


# ws fro websocket to distiinguish b/w HTTTP connection
# ChatroomConsumer class initilized with as_asgi() method

websocket_urlpatterns = [
    path('ws/chatroom/<str:chatroom_name>',ChatroomConsumer.as_asgi()),
    path("ws/quiz/<str:quiz_id>/", QuizConsumer.as_asgi()),
]