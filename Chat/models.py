from django.db import models
from django.conf import settings
import shortuuid

# Here settings.AUTH_USER_MODEL = Users.User


def generate_group_name():
    return shortuuid.uuid()
class ChatGroup(models.Model):
    group_name = models.CharField(max_length=128, unique=True,default=generate_group_name)
    groupchat_name = models.CharField(max_length=128, null=True, blank=True)
    admin = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='groupchats',blank=True, null=True, on_delete=models.SET_NULL)
    # Group Names are created dynamically so default will be UUID
    users_online = models.ManyToManyField(settings.AUTH_USER_MODEL,related_name='online_in_groups',blank=True)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='chat_groups',blank=True)
    is_private = models.BooleanField(default=False)
    # Public chat will not have members

    def __str__(self):
        return self.group_name
    

class GroupMessage(models.Model):
    group = models.ForeignKey(ChatGroup,related_name='chat_messages', on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    body = models.CharField(max_length=300)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.author.username} : {self.body}'
    
    class Meta:
        ordering = ['-created_at']
