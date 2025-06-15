from django.urls import path,include
from .views import user_signup,user_login,set_encryption_key,home,download_encryption_key,APIKeyStoreViewset,decrypt_apikey,user_logout
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'apikey', APIKeyStoreViewset, basename='apikey-store')

urlpatterns = [
    path('signup/',user_signup,name='signup'),
    path('login/',user_login,name='login'),
    path('logout/',user_logout,name='logout'),
    path('set-key/', set_encryption_key, name='set_encryption_key'),
    path('home/',home,name='home'),
    path('download-key/', download_encryption_key, name='download_encryption_key'),
    path('decrypt-apikey/', decrypt_apikey, name='decrypt-apikey'),
    path('', include(router.urls)),
]