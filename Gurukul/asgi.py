"""
ASGI config for Gurukul project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Gurukul.settings')

# Add router that can also  handle websockets along with http requests
# Add the HTTTP connection in the router itself

from . import routing

application = ProtocolTypeRouter({
    'http':get_asgi_application(),
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(URLRouter(routing.websocket_urlpatterns))
    )
})
'''
AllowedHostsOriginValidator: Security feature that allows connections from those hosts that are listed in allowed host setting
AuthMiddlewareStack: Django Middleware using django authentication system to give us access to the logged-in user
URLRouter: Map the URL to the correct function in the backend using routing.py file
routing.py file is imported after we calling the get_asgi_applicaition() function
SUCCESSFULLY configured a HTTP and websocket connection
'''


