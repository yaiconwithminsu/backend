import time
import os
import torchaudio
import torch
from threading import Thread, Lock
from django.shortcuts import render
from .models import User
from django.http import HttpResponse, JsonResponse, FileResponse
from django.views import View
from django.core.files.base import ContentFile
from django.core.files.storage import FileSystemStorage
from shutil import copyfile
from infer import convert_audio

from infer_tools.infer_tool import Svc


model_chim = Svc('minsu', './checkpoints/minsu/config.yaml', True, './checkpoints/minsu/model_ckpt_steps_6000.ckpt')
user_list = {}
lock = Lock()

class UsersView(View):
    def get(self, request):
        current_id = int(request.GET['id'])
        print('id :', current_id)
        
        if current_id > 0:
            return HttpResponse(user_list[current_id].finish, status=200)
        elif current_id == 0:
            return HttpResponse(True, status=200)
        else:
            file_path = user_list[-current_id].music_file_converted.path
            audio = open(file_path, 'rb')
            return FileResponse(audio)

    def post(self, request):
        current_id = len(User.objects.all()) + 1
        thread = Thread(target=convert, args=[current_id])
        user = User(id=current_id,
                    finish=False,
                    music_file=request.FILES['audio'],
                    name=request.POST['name'])
        user_list[current_id] = user
        user.save()
        # 모델 돌려야 함
        thread.start()
        print('id :', user)
        return HttpResponse(current_id, status=200)


def convert(id):
    # Getting Filename
    user = user_list[id]
    path = user.music_file.name
    sp = path.split('.')
    converted_path = sp[0] + '_converted.wav'
    print('start converting', path, 'to', converted_path)

    # We are using only one GPU, in race condition
    # using mutex to make an critical section
    lock.acquire()
    
    # Voice & Accompaniment split
    os.system(f'spleeter separate ./media/{path} -p spleeter:2stems -o ./media/user_{user}/')
    
    voice_path = f'./media/{sp[0]}/vocals.wav'
    accomp_path = f'./media/{sp[0]}/accompaniment.wav'

    voice_converted_path = f'./media/{sp[0]}/vocals_converted.wav'

    # SVC
    print('start SVC')
    convert_audio(voice_path, voice_converted_path, model_chim)

    # End of critical section
    # Below this, this thread will never use GPU
    lock.release()

    print('start Combine')
    # Combine Voice & Accompaniment
    sound_voice_converted, srn_voice = torchaudio.load(voice_converted_path)
    sound_accomp, srn_accomp = torchaudio.load(accomp_path)
    accomp_size = sound_accomp.size(dim = 1)
    voice_size = sound_voice_converted.size(dim = 1)
    accomp_ch = sound_accomp.size(dim = 0)
    voice_ch = sound_voice_converted.size(dim = 0)
    
    if accomp_ch != voice_ch:
        # Channel Num Conflict -> Convert to Mono Channel
        sound_voice_converted = sound_voice_converted.mean(dim=0).view(1, -1)
        sound_accomp = sound_accomp.mean(dim=0).view(1, -1)
        accomp_ch = 1
        voice_ch = 1

    if accomp_size != voice_size:
        # Sound Length Conflict
        sound_len = max(accomp_size, voice_size)
        combined_sounds = torch.zeros(accomp_ch, sound_len).float()
        combined_sounds[:, :accomp_size] += sound_accomp
        combined_sounds[:, :voice_size] += sound_voice_converted      
    else :
        combined_sounds = sound_voice_converted + sound_accomp
    if srn_voice != srn_accomp:
        print("ERROR, frequency conflicts")
    
    torchaudio.save('./media/' + converted_path, combined_sounds, srn_accomp)
    

    # Save at Database
    user.music_file_converted.name = converted_path
    user.finish = True
    user.save(update_fields=['music_file_converted', "finish"])
