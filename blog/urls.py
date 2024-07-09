from django.urls import path
from blog import views


app_name = "blog"

urlpatterns = [
    path("article/<int:pk>/", views.ArticleDetailView.as_view(), name="detail"),
]
