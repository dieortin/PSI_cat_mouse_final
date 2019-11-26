import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mouse_cat.settings')
django.setup()


from datamodel.models import *

user10 = User.objects.get_or_create(id=10, username="user10")[0]
user11 = User.objects.get_or_create(id=11, username="user11")[0]
game = Game(cat_user=user10)
game.save()

query_result = Game.objects.filter(mouse_user=None)
print(query_result)
first_result = query_result.order_by("id")[0]

first_result.mouse_user = user11
first_result.save()
print(first_result)
first_result.cat2 = 11
first_result.save()
print(first_result)
first_result.mouse = 52
first_result.save()
print(first_result)
