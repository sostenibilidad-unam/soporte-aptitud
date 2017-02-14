# -*- coding: utf-8 -*-
from Crypto.Random.random import choice
from cProfile import label
from django import forms
from ordenamiento.models import Actividad, Mapa_Valor
import lib.GrassShell as gsh
import ordenamiento.querys as q
import operator
import lib.U as U
import lib.D as D 
from django.contrib.auth.models import User

class AdminViewProgramForm(forms.Form):
    programa_id = forms.CharField()         
    def __init__(self, *args, **kwargs):                
        super(AdminViewProgramForm, self).__init__(*args, **kwargs)
        
    