from rest_framework import generics, permissions
from .models import Project, File
from .serializers import ProjectSerializer, FileSerializer

class ProjectListCreateView(generics.ListCreateAPIView):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Project.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class FileListUpdateView(generics.ListCreateAPIView):
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        project_id = self.kwargs['pid']
        return File.objects.filter(project__id=project_id, project__user=self.request.user)

    def perform_create(self, serializer):
        project = Project.objects.get(id=self.kwargs['pid'], user=self.request.user)
        serializer.save(project=project)

class FileRetrieveUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = FileSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        project_id = self.kwargs['pid']
        return File.objects.filter(project__id=project_id, project__user=self.request.user)

