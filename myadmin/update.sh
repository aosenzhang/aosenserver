#! /usr/bin/ bash
#更新数据库命令
#python manage.py createsuperuser
python manage.py makemigrations myapp
python manage.py migrate
