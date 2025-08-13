from django.urls import path
from .views import MessageSend, OTPCodeSend ,Authentication, SessionList

app_name = 'drfchelseru'

urlpatterns = [
    path('message/send/', MessageSend.as_view(), name='message-send'),
    path('otp/send/', OTPCodeSend.as_view(), name='otp-send'),
    path('authenticate/', Authentication.as_view(), name='auth'),
    path('sessions/', SessionList.as_view(), name='sessions'),
]
