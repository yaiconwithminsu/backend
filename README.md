# SVC Backend Server
cloned and edited [link](https://github.com/prophesier/diff-svc)

### requirements - using conda env recommended

```
conda install pytorch torchvision torchaudio pytorch-cuda=11.8 -c pytorch -c nvidia

pip install django
```

[link](https://github.com/yaiconwithminsu/model) 를 참고해 requirements.txt 설치



### running server
```
python manage.py runserver
```

### issues
업로드하는 파일 이름에 .이 두 개 이상 포함되어있으면 오류 발생
