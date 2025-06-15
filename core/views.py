from django.shortcuts import render,redirect
from .forms import SignupForm,LoginForm
from django.contrib.auth import authenticate, login,logout
from rest_framework.viewsets import ViewSet
from .models import APIKeyStore
from rest_framework.response import Response
from rest_framework import status
from .serializers import APIKeyStoreSerializer
from .utils import encrypt,decrypt,generate_encryption_key
from rest_framework.decorators import api_view, permission_classes
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required
from rest_framework.permissions import IsAuthenticated
from django.urls import reverse
# Create your views here.


def user_signup(request):
    if request.method == 'POST':
        form = SignupForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = SignupForm()
    return render(request, 'core/signup.html', {'form': form})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            user = authenticate(request, email=email, password=password)
            if user:
                login(request, user)    
                if user.is_first_login:
                    key = generate_encryption_key()
                    request.session['encryption_key'] = key
                    request.session['show_download_prompt'] = True

                    user.is_first_login = False
                    user.save()

                return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'core/login.html', {'form': form})

def user_logout(request):
    request.session.pop('encryption_key', None)
    logout(request)
    return redirect('login')


class APIKeyStoreViewset(ViewSet):

    permission_classes = [IsAuthenticated]

    def list(self,request):
        user = request.user
        try:
            apikeys = APIKeyStore.objects.filter(user=user)
        except APIKeyStore.DoesNotExist:
            return Response({"Message": "User Not Found"},status=status.HTTP_400_BAD_REQUEST)
        serializer = APIKeyStoreSerializer(apikeys, many=True)
        return Response({"keys": serializer.data},status=status.HTTP_200_OK)


    def create(self,request):
        data = request.data.copy()
        data['user'] = request.user.id
        print(data['user'])
        key = request.session.get('encryption_key')

        if not key:
            return Response({"error": "Encryption key not set in session"}, status=400)
        
        data['apikey'] = encrypt(key=key,plain_message=data['apikey'])
        print(data['apikey'])
        serializer = APIKeyStoreSerializer(data=data)
        if serializer.is_valid():
            post_serializer = serializer.save()
            print(post_serializer)
        else:
            return Response({"error": serializer.errors})
        return Response({"Message":"APIKEY Stored successfully", "redirect_url": reverse("home")})
            


    def destroy(self,request,pk):
        user = request.user.id
        apikey = APIKeyStore.objects.get(user=user,id=pk)
        apikey.delete()
        return Response({"Message":"APIKEY Deleted Successfully"})

    def retrieve(self, request, pk=None):
        user = request.user.id
        try:
            apikey = APIKeyStore.objects.get(user=user, id=pk)
        except APIKeyStore.DoesNotExist:
            return Response({"error": "Not Found"}, status=404)
        serializer = APIKeyStoreSerializer(apikey)
        return Response({
            "message": "API Key fetched successfully",
            "apikey": serializer.data
        })


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def set_encryption_key(request):
    key = request.POST.get('encryption_key')  
    request.session['encryption_key'] = key
    return Response({"message": "Encryption key stored in session"})


@login_required
def home(request):
    apikeys = APIKeyStore.objects.filter(user=request.user)
    show_prompt = request.session.pop('show_download_prompt', False)
    return render(request, 'core/home.html', {'show_download_prompt': show_prompt, 'apikeys': apikeys})


@login_required
def download_encryption_key(request):
    key = request.session.get('encryption_key')

    if not key:
        return HttpResponse("No encryption key available or already downloaded.", status=404)

    response = HttpResponse(key, content_type='text/plain')
    response['Content-Disposition'] = 'attachment; filename="encryption_key.txt"'

    if 'show_download_prompt' in request.session:
        del request.session['show_download_prompt']

    return response


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def decrypt_apikey(request):
    key = request.session.get('encryption_key')
    id = request.data.get('id')


    try:
        apikey_obj = APIKeyStore.objects.get(user=request.user, id=id)
        decrypted_key = decrypt(key=key, encrypted_message=apikey_obj.apikey)
        return Response({'decrypted_apikey': decrypted_key})
    except APIKeyStore.DoesNotExist:
        return Response({'error': 'API key not found'}, status=404)
    except Exception as e:
        return Response({'error': str(e)}, status=400)
