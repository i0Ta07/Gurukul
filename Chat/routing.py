from django.urls import path
from .consumers import *
# consumers.py = views.py but for websocket connection, it contains the busssiness logic of the applicaiton

websocket_urlpatterns = [
    path('ws/chatroom/<chatroom_name>',ChatroomConsumer.as_asgi()),
    # ws fro websocket to distiinguish b/w HTTTP connection
    # ChatroomConsumer class initilized with as_asgi() method

]