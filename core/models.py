from django.db import models
from django.contrib.auth.models import AbstractBaseUser,PermissionsMixin,BaseUserManager
from django.utils import timezone
# Create your models here.

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError(_("The Email must be set"))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

class User(AbstractBaseUser,PermissionsMixin):
    email = models.EmailField(unique=True)
    date_joined = models.DateTimeField(default=timezone.now)
    is_first_login = models.BooleanField(default=True)


    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.email}"


class APIKeyStore(models.Model):
    user = models.ForeignKey(User,on_delete=models.CASCADE)
    provider = models.CharField(max_length=256,unique= True)
    apikey = models.CharField(max_length=256,unique =True)
    description = models.TextField(blank=True,null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

