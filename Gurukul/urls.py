"""
URL configuration for Gurukul project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include


# Whenever some URL comes go in Users.urls instead of 
# directly returning a function and we handle it from there
# this is making it less complex and understandable 

urlpatterns = [
    path('admin/', admin.site.urls),
    path('',include('Users.urls')),
    path('chat/',include('Chat.urls')), # Chatt app home will be displayed as chat/home

]
