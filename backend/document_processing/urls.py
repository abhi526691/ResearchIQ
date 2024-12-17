from django.urls import path
from .views import *

urlpatterns = [
    path('file/', InformationExtractor.as_view()),
    path('qna/', QnAView.as_view()),
    path('summary/', SummarizerView.as_view())
]
