from .consumers import CodeRunConsumer
from django.urls import re_path

websocket_urlpatterns = [
    re_path(r'ws/projects/(?P<pid>\d+)/run/$', CodeRunConsumer.as_asgi()),
]
