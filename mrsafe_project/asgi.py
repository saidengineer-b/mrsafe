"""
ASGI config for quiz_project project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import mrsafe.routing  # ✅ Ensure your app’s routing exists

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quiz_project.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            mrsafe.routing.websocket_urlpatterns  # ✅ Ensure this is imported correctly
        )
    ),
})
