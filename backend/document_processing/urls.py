from django.urls import path
from .views import *

urlpatterns = [
    path('file/', InformationExtractor.as_view()),
    path('qna/', QnA.as_view())
]
