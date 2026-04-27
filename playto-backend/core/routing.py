from django.urls import re_path
from core.consumers import PayoutConsumer

websocket_urlpatterns = [
    re_path(r"ws/payouts/$", PayoutConsumer.as_asgi()),
]