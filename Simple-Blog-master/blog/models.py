from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from tags.models import Tag
import sys,os

sys.path.append(os.getcwd())
# blog models
animals = {}
with open('pro_animals.txt','rb') as file:
    for animal_data in file:
        name, id = animal_data.split(';')
        animals[str(id).strip()] = str(name)
file.close()

class Animal(models.Model):
    name = models.CharField(max_length=220)
    description = models.CharField(max_length=520)
    owner = models.ForeignKey(User)
    tags = models.ManyToManyField(Tag)
    # user = models.CharField(max_length=220)
    # net_id = models.CharField(max_length=220)


lines = []
for id in animals:
    name = animals[id]
    lines.append('%s;%s'%(name,id))
animals_ = []
for line in sorted(lines):
    name,id = line.split(';')
    animals_.append((name,id))
