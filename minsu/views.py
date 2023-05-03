from django.shortcuts import render
from .models import User
from django.http import HttpResponse, JsonResponse
from django.views import View


user_list = {}

class UsersView(View):
    def get(self, request):
        return HttpResponse(user_list[request.GET['id']].finish)

    def post(self, request):
        user = User(id=request.POST['id'],
                    finish=False,
                    music_file=request.FILES.get('music_file'))
        user_list[user.id] = user
        # 모델 돌려야 함
        user.finish = True
        user.save()
        print(user)
        return HttpResponse(status=200)
