# -*- coding: utf-8 -*-
from django import forms
from django.forms.models import ModelForm
from lib.D import ROL
from ordenamiento.models import Programa, Sector, User_Programa_Sector, \
    Mapset, MapsetAdmin
import lib.GrassShell as gsh
import programa.querys as q
from datetime import date

class SearchMovementsFrom(ModelForm):

    error_messages = {'invalid':"El campo no es valido", 'required':"El campo es requerido"}
    
    user = forms.CharField(label="*Usuario:", error_messages=error_messages)
    accion = forms.CharField(label="*Accion:", error_messages=error_messages)
    fecha_desde = forms.DateField(label="*Desde:", error_messages=error_messages)
    fecha_hasta = forms.DateField(label="*Hasta:", error_messages=error_messages)
                 
    def clean_fecha_desde(self):
        f = self.cleaned_data["fecha_desde"]        
        hoy = date.today()
        fecha = date(f.year,f.month,f.day)
        return f
         
    class Meta:
        model = Programa
        fields = ('user', 'fecha_desde', 'fecha_hasta')
                
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('usuarios', None)
        self.accion = kwargs.pop('acciones', None)
        super(SearchMovementsFrom, self).__init__(*args, **kwargs)        
          
        self.fields['user'].widget = forms.Select(choices=self.user, attrs={'style': 'width:100px'})        
        self.fields['accion'].widget = forms.Select(choices=self.accion, attrs={'style': 'width:100px'})
     
       