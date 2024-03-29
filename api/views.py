# Create your views here.
from rest_framework import generics, permissions
from .serializers import TodoSerializer, TodoToggleCompleteSerializer
from todo.models import Todo
from django.db import IntegrityError
from django.contrib.auth.models import User
from rest_framework.parsers import JSONParser
from rest_framework.authtoken.models import Token
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate

class TodoListCreate(generics.ListCreateAPIView): 

    # The serializer class that should be used for validating and 
    # deserializing input, and for serializing output
    # We specify TodoSerializer which we have earlier implemented
    serializer_class = TodoSerializer
    # permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user        
        # return Todo.objects.filter(user=user).order_by('-created')
        if user.is_authenticated:
            return Todo.objects.filter(user=user).order_by('-created')
        else:
            # If the user is not authenticated, return an empty queryset
            return Todo.objects.none()

    def perform_create(self, serializer):
        #serializer holds a django model
        serializer.save(user=self.request.user) 

class TodoRetrieveUpdateDestroy(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TodoSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        # user can only update, delete own posts
        return Todo.objects.filter(user=user)

class TodoToggleComplete(generics.UpdateAPIView):
    serializer_class = TodoToggleCompleteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        return Todo.objects.filter(user=user)

    def perform_update(self,serializer):
        serializer.instance.completed=not(serializer.instance.completed)
        serializer.save()

@csrf_exempt
def signup(request):
    if request.method == 'POST':
        try:
            data = JSONParser().parse(request) # data is a dictionary
            user = User.objects.create_user(
                data['username'],
                password=data['password'])
            user.save()

            token = Token.objects.create(user=user)
            return JsonResponse({'token':str(token)},status=201) 

        except IntegrityError:
            return JsonResponse({
                'error':'username taken. choose another username'},
                status=400)

@csrf_exempt
def login(request):
    if request.method == 'POST':        
        data = JSONParser().parse(request)
        user = authenticate(
                request,
                username=data['username'],
                password=data['password'])
        if user is None:
            return JsonResponse({'error':'unable to login. check username and password'},status=400)
        else:     # return user token
            try:
                token = Token.objects.get(user=user)
            except: # if token not in db, create a new one
                token = Token.objects.create(user=user)
            return JsonResponse({'token':str(token)},status=201)  