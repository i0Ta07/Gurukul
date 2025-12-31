from django.shortcuts import render,get_object_or_404,redirect
from django.contrib.auth.decorators import login_required
from .models import *
from .forms import *
from django.contrib.auth import get_user_model
from django.http import Http404
from django.contrib import messages
# Verif the email dadress either on registration or on profile settings

User = get_user_model()

@login_required(login_url='login')
def chat_home(request,chatroom_name = 'public-chat'): # will display the public chat if name is not given
    chat_group = get_object_or_404(ChatGroup,group_name = chatroom_name)
    chat_messages = chat_group.chat_messages.all()[:30]
    form = chat_message_create_form()

    other_user = None
    if chat_group.is_private:
        if request.user not in chat_group.members.all():
            raise Http404()
        for member in chat_group.members.all(): # get the other user for template
            if member != request.user:
                other_user = member
                break

    # Share the group using the URL
    if chat_group.groupchat_name:
        if request.user not in chat_group.members.all():
            chat_group.members.add(request.user)

    if request.htmx: # Still a POST req but of htmx
        form = chat_message_create_form(request.POST) # Create the form element with the new post data
        print("HTMX POST received")
        if form.is_valid():
            message = form.save(commit=False) # to get the form instance and attach author and group then save
            message.author = request.user
            message.group = chat_group
            message.save()
            return render(request,'Chat/partials/chat_message_partial.html',{
                'message':message, # context with new msg send to partial htmx along with user
                'user' : request.user # We need to check if the author of the msg is the logged in user
            })
    context={
        'chat_messages':chat_messages,
        'form':form,
        'other_user' : other_user,
        'chatroom_name': chatroom_name,
        'chat_group':chat_group,
    }
    
    return render(request,'Chat/chat_home.html',context)

@login_required(login_url='login')
def get_or_create_chatroom(request,username):
    if request.user.username == username:
        return redirect('chat_home')
    
    
    
    other_user = User.objects.get(username=username)
    my_chatrooms = request.user.chat_groups.filter(is_private = True)
    if my_chatrooms:
        for chatroom in my_chatrooms:
            if other_user in chatroom.members.all():
                chatroom = chatroom
                break
            else:
                chatroom = ChatGroup.objects.create(is_private = True)
                chatroom.members.add(other_user,request.user)

    else:
        chatroom = ChatGroup.objects.create(is_private = True)
        chatroom.members.add(other_user,request.user)

    return redirect('chatroom',chatroom.group_name)

@login_required(login_url='login')
def create_groupchat(request):
    form = new_group_form()

    if request.method == 'POST':
        form =  new_group_form(request.POST)
        if form.is_valid():
            new_groupchat = form.save(commit=False)
            new_groupchat.admin = request.user
            new_groupchat.save()
            new_groupchat.members.add(request.user)
            return redirect('chatroom',new_groupchat.group_name)
    context = {
        'form':form
    }
    return render(request,'Chat/create_groupchat.html',context)

@login_required(login_url='login')
def edit_chatroom(request,chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name = chatroom_name)
    if request.user != chat_group.admin:
        raise Http404()
    
    form = edit_chatroom_form(instance = chat_group)
    if request.method == 'POST':
        form = edit_chatroom_form(request.POST,instance = chat_group)
        if form.is_valid():
            form.save()
            remove_members = request.POST.getlist('remove_members')
            for member_id in remove_members:
                member = User.objects.get(id= member_id)
                chat_group.members.remove(member)

            return redirect('chatroom', chat_group.group_name)


    context = {
        'form': form,
        'chat_group' : chat_group
    }

    return render(request,'Chat/edit_chatroom.html',context)


@login_required(login_url='login')
def delete_chatroom(request, chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name = chatroom_name)
    if request.user != chat_group.admin:
        raise Http404()
    
    if request.method == "POST":
        chat_group.delete()
        messages.success(request,'Chatroom deleted successfully')
        return redirect('user_friends_list')
    
    context={
        'chat_group': chat_group
    }

    return render(request, 'Chat/delete_chatroom.html',context)

@login_required(login_url='login')
def leave_chatroom(request,chatroom_name):
    chat_group = get_object_or_404(ChatGroup, group_name = chatroom_name)
    if request.user not in chat_group.members.all():
        raise Http404()
    
    if request.method  == 'POST':
        chat_group.members.remove(request.user)
        messages.success(request,'You have left the Chatroom')
        return redirect('user_friends_list')