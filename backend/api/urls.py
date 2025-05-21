from django.urls import path
from .views import (
    ProjectListCreateView,
    FileListUpdateView,
    FileRetrieveUpdateDeleteView
)

urlpatterns = [
    path('projects/', ProjectListCreateView.as_view(), name='project-list'),
    path('projects/<int:pid>/files/', FileListUpdateView.as_view(), name='file-list-create'),
    path('projects/<int:pid>/files/<int:pk>/', FileRetrieveUpdateDeleteView.as_view(), name='file-detail'),
]