from .models import APIKeyStore
from rest_framework.serializers import ModelSerializer


class APIKeyStoreSerializer(ModelSerializer):

    class Meta:
        model = APIKeyStore
        fields = "__all__"