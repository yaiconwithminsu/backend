from django.shortcuts import render
from .models import User
from django.http import HttpResponse, JsonResponse, FileResponse
from django.views import View
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from shutil import copyfile


user_list = {}

class UsersView(View):
    def get(self, request):
        current_id = int(request.GET['id'])
        print('id :', current_id)
        
        if current_id > 0:
            return HttpResponse(user_list[current_id].finish, status=200)
        else:
            file_path = user_list[-current_id].music_file_converted.path
            audio = open(file_path, 'rb')
            return FileResponse(audio)

    def post(self, request):
        current_id = len(User.objects.all()) + 1
        user = User(id=current_id,
                    finish=False,
                    music_file=request.FILES['audio'],
                    name=request.POST['name'])
        user_list[current_id] = user
        user.save()

        # 모델 돌려야 함
        convert(current_id)

        print('id :', user)
        return HttpResponse(current_id, status=200)

def convert(id):
    user = user_list[id]
    path = user.music_file.name
    sp = path.split('.')
    converted_path = sp[0] + '_converted.' + sp[1]
    print(path, 'to', converted_path)

    # the converting process should be located here
    # the converted file should be saved at convereted_path
    copyfile('./media/' + path, './media/' + converted_path)
    

    user.music_file_converted.name = converted_path;
    user.finish = True
    user.save(update_fields=['music_file_converted'])