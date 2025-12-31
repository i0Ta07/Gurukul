from channels.generic.websocket import WebsocketConsumer
from django.shortcuts import get_object_or_404
from django.template.loader import render_to_string
from .models import *
from asgiref.sync import async_to_sync
import json
# WebsocketConsumer handling the websocket connection,
# We got the generic one and will customize it like user from Abstract uiser

class ChatroomConsumer(WebsocketConsumer):
    
    def connect(self):
        self.user = self.scope['user']
        self.chatroom_name = self.scope['url_route']['kwargs']['chatroom_name']
        self.chatroom = get_object_or_404(ChatGroup, group_name= self.chatroom_name)

        '''
        To add the channel to the group for multi-way communication
        Channel name generated automatically by the server andd identifies a unqiue user
        Channel layer is async operation so we have to create the whole method async
        so we will inherit from Async websocket consumer, use async the connect method 
        and await to the channel layer operation and accept().

        Simpler approch is to user async_to_sync 
        '''
        async_to_sync(self.channel_layer.group_add)(
            self.chatroom_name, self.channel_name
        )

        # add and update online users
        if self.user not in self.chatroom.users_online.all():
            self.chatroom.users_online.add(self.user)
            self.update_online_count()
        self.accept()

    # To leave the chat group when the channel disconnects 
    def disconnect(self, close_code):
        async_to_sync(self.channel_layer.group_discard)(
            self.chatroom_name, self.channel_name
        )

        # remove and update online users
        if self.user in self.chatroom.users_online.all():
            self.chatroom.users_online.remove(self.user)
            self.update_online_count() # function to update the count in all the users browsers

    def receive(self, text_data=None):
        # this method receives the data in text_data in JSON  format, convert to python obj
        text_data_obj = json.loads(text_data)
        body = text_data_obj['body']
        # Message is saved to DB
        message = GroupMessage.objects.create(
            body = body,
            author = self.user,
            group = self.chatroom
        )
        # AFter save call send to send the data back to frontend to display the msg in thr form of html partial

        # Event dictionary send to message handler
        # To send the htmx partial to everyone in the group we have to create an event
        event = {
            'type':'message_handler', # to connect to message_handler we add the keyword argument type 
            'message_id':message.id,
        }
        # Replacing the self.send function as we broadcasting the msg to everyone in the group
        # The group_send sends the same event to all members in the group,
        # The message_handler renders a individual code partial for each user.
        async_to_sync(self.channel_layer.group_send)(
            self.chatroom_name, event
        )

    def message_handler(self, event):
        # From the Event dictionary
        message_id = event['message_id']
        message = GroupMessage.objects.get(id=message_id)
        # In HTTP render, in WS we have render_to_string
        context={
            'message' : message,
            'user': self.user,
        }
        html = render_to_string('Chat/partials/chat_message_partial.html',context=context)
        # To display this partial on the page we need to use the Out of band attribute (OOB) as we have no hx-swap and hx-target attribute for WS
        # We will define it in the partail itself
        self.send(text_data=html)


    def update_online_count(self):
        online_count = self.chatroom.users_online.count() -1
        #Broadcast his number to all the users in the chatroom
        event = {
            'type':'online_count_handler', # Method that will handle the response
            'online_count':online_count
        }
        # event is the data we are sending back to the browser
        async_to_sync(self.channel_layer.group_send)(self.chatroom_name, event)

    def online_count_handler(self,event):
        online_count = event['online_count']
        context = {
            'online_count':online_count,
            'chat_group':self.chatroom
        }
        # handler sending the data to the partial
        html = render_to_string('Chat/partials/online_count.html',context)
        self.send(text_data=html) # serrialize the html partial and send it back to the client
        


        

