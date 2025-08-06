import random
from datetime import timedelta
from django.utils import timezone
from django.db import models
from django.conf import settings
from django.contrib.auth.models import AbstractUser, AbstractBaseUser, PermissionsMixin
from django.db.models.signals import post_save


class User(AbstractUser):
    otp = models.CharField(max_length=6, blank=True, null=True)
    otp_exp = models.DateTimeField(blank=True, null=True) 
    otp_verified = models.BooleanField(default=False)
    max_try_top = settings.MAX_OTP_TRY
    otp_attempts = models.IntegerField(default=0)
    block_until = models.DateTimeField(blank=True, null=True)

    def generate_otp(self):
        self.otp = str(random.randint(100000, 999999))
        self.otp_exp = timezone.now() + timedelta(minutes=1)
        self.otp_verified = False
        self.otp_attempts = 0  # сброс попыток при генерации нового OTP
        self.save()

    def is_blocked(self):
        if self.block_until and self.block_until > timezone.now():
            return True
        return False

    def increment_attempts(self):
        self.otp_attempts += 1
        if self.otp_attempts >= self.max_try_top:
            # блокируем пользователя на 1 минуту
            self.block_until = timezone.now() + timedelta(minutes=1)
        self.save()

    def reset_attempts(self):
        self.otp_attempts = 0
        self.block_until = None
        self.save()


    username = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username 



class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)

    full_name = models.CharField(max_length=300)
    bio = models.CharField(max_length=300)
    #image = models.ImageField(default='default.jpg', upload_to='user_images')
    verified = models.BooleanField(default=False)

    def __str__(self):
        return self.full_name
    

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()

post_save.connect(create_user_profile, sender=User)
post_save.connect(save_user_profile, sender=User)    