from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User as default_user
from django.utils.timezone import now, timedelta
from random import randint
from .settings import auth_init_check

UserGet = get_user_model()

class User(models.Model):
    user = models.OneToOneField(default_user, on_delete=models.CASCADE, related_name='mobile_drf_chelseru')
    mobile = models.CharField(max_length=11)
    group = models.IntegerField(default=0, help_text='choice group type or user level, with numbers.')

    def __str__(self):
        return f'{self.user.username} | {self.mobile}'


class OTPCode(models.Model):
    code = models.CharField(max_length=10)
    mobile_number = models.CharField(max_length=11)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.code} -> {self.mobile_number} | {self.created_at}'

    def save(self, *args, **kwargs):
        """
        Generates a new random code if one does not already exist.
        """
        if not self.code:
            icheck = auth_init_check()
            if icheck and isinstance(icheck, dict):
                otp_len = icheck['OPTIONS']['len']
                otp_exp_time = icheck['OPTIONS']['exp_time']

                self.code = str(randint(int('1' + (otp_len - 1) * '0'), int(otp_len * '9')))
        super().save(*args, **kwargs)

    def check_code(self):
        try:
            icheck = auth_init_check()
            if icheck and isinstance(icheck, dict):
                otp_exp_time = icheck['OPTIONS']['exp_time']
                if now().timestamp() <= (self.created_at + timedelta(seconds=otp_exp_time * 60)).timestamp():
                    self.delete()
                    return True
                self.delete()
        except:
            pass
        return False


class Session(models.Model):
    user = models.ForeignKey(default_user, models.DO_NOTHING, related_name='session_drf_chelseru')
    session_key = models.CharField(max_length=40, unique=True)
    user_agent = models.TextField()
    ip_address = models.GenericIPAddressField()
    device = models.TextField()
    browser = models.TextField()

    last_seen = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add = True)

    def __str__(self):
        return f'{self.user} - {self.ip_address}'


class MessageSMS(models.Model):
    message_text = models.TextField()
    mobile_number = models.CharField(max_length=20)
    _from = models.CharField(max_length=20, blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)

    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'to: {self.mobile_number} , at: {self.created_at}'
    


class ChatRoom(models.Model):
    user_1 = models.ForeignKey(UserGet, on_delete=models.CASCADE, related_name='user1_chats_drf_chelseru')
    user_2 = models.ForeignKey(UserGet, on_delete=models.CASCADE, related_name='user2_chats_drf_chelseru')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"ID: {self.id} | Chat between {self.user_1.username} and {self.user_2.username}"


class MessageChat(models.Model):
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages_chat_drf_chelseru')
    sender = models.ForeignKey(UserGet, on_delete=models.CASCADE)
    text = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"iD: {self.id} | Message from {self.sender.username} at {self.timestamp} | Chatroom ID: {self.chat_room.id}"