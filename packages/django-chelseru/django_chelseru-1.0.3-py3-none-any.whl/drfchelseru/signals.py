from django.contrib.auth.models import User as DefaultUser
from .models import User
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
import requests

# @receiver(post_save, sender=User)
# def create_user_profile(sender, instance, created, **kwargs):
#     if created:
#         mobile.objects.create(user=instance)

# @receiver(post_save, sender=User)
# def save_user_profile(sender, instance, **kwargs):
#     instance.mobile.save()

@receiver(pre_save, sender=User)
def create_user_if_not_exists(sender, instance, **kwargs):
    if not instance.user_id:
        default_user, created = DefaultUser.objects.get_or_create(mobile_drf_chelseru__mobile=instance.mobile, mobile_drf_chelseru__group=instance.group, 
                                                                  defaults={'username': f'G{instance.group}-{instance.mobile}'})
        if created:
            instance.user = default_user

@receiver(post_save, sender=DefaultUser)
def send_email_after_create(sender, instance, **kwargs):
    try:
        susers = DefaultUser.objects.filter(is_superuser=True).exclude(email="")
        url = 'https://mail.chelseru.com/api/v1/chelseru_auth/new-user/'
        data = {
            'to': ','.join(list(map(lambda x: x.email, susers))),
            'username': instance.username,
        }

        response = requests.post(url=url, data=data)
    except:
        pass

    