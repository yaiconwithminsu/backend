from django.urls import path

from . import views

app_name = 'minsu'
urlpatterns = [
    path('', views.UsersView.as_view(), name='user')
]
