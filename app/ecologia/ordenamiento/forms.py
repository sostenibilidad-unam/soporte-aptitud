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

class SectorForm(forms.Form):
    sector = forms.CharField(widget=forms.Select(choices=[]))         
    def __init__(self, *args, **kwargs):
        self.id = kwargs.pop('id', None)
        self.programa_id = kwargs.pop('programa_id', None)        
        super(SectorForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['sector']
                
        self.fields['sector'].widget = forms.Select(choices=q.get_idUserProgramaSector_nombreSector(self.id,self.programa_id))

class ActividadAtributoForm(forms.Form):
    actividad = forms.CharField(widget=forms.Select(choices=[]))
    atributo = forms.CharField(widget=forms.Select(choices=[]))    
    def __init__(self, *args, **kwargs):   
        self.id = kwargs.pop('id', None)     
        super(ActividadAtributoForm, self).__init__(*args, **kwargs)
        self.fields.keyOrder = ['actividad', 'atributo']       
        
        act = q.getActividad(self.id)       
        if not act:            
            self.peso = ''
            self.atributo = ''
        else:
            atr = q.getAtributo(act[0][0])            
            self.fields['actividad'].widget = forms.Select(choices=act)        
            self.fields['atributo'].widget = forms.Select(choices=atr)
            self.peso = q.getPeso(act[0][0])[0][1]
            self.atributo = atr[0][0]
        
    def getPeso(self):
        return self.peso
        
    def getAtributo(self):
        return self.atributo

    
    
class ActividadForm(forms.Form):
    
    error_messages = {'required':"Proporcione un nombre a la actividad"} 
    
    actividad = forms.CharField(error_messages=error_messages)        
    def clean_actividad(self):
        actividad = self.cleaned_data["actividad"]       
        
        if Actividad.objects.filter(actividad=actividad,user_sector_programa=self.usp_id).exists():
            raise forms.ValidationError("La actividad %s esta ocupado" % actividad)
        else:
            return actividad
    
    def __init__(self, *args, **kwargs):   
        self.usp_id = kwargs.pop('usp_id', None)
        super(ActividadForm, self).__init__(*args, **kwargs)  
             
    def save(self,commit=True):        
        actividad = self.cleaned_data['actividad']
        
        if commit:
            a = Actividad(actividad=actividad, user_sector_programa_id=self.usp_id)
            a.save()            
            return a

class UserForm(forms.Form):
    usuario = forms.CharField(widget=forms.Select(choices=[]))         
    def __init__(self, *args, **kwargs):                
        self.choices = kwargs.pop('choices', None)
        super(UserForm, self).__init__(*args, **kwargs)
        #self.fields.keyOrder = ['username']                
        self.fields['usuario'].widget = forms.Select(choices=self.choices)

        
"""
    Comandos
"""

class ComandosForm(forms.Form):
    lst_comando = ((D.CMD.DESAGRUPAR, "Desagrupar"), (D.CMD.DISTANCIA, "Distancia"), (D.CMD.ESTADISTICA, "Estadísticas"), (D.CMD.PENDIENTE, "Pendiente"),  (D.CMD.NULOS, "Nulos")) 
    lst_tipo = ((D.CMD_ATTR.GRADOS, "grados"), (D.CMD_ATTR.PORCENTAJE, "porcentaje"))
    
    
    comando = forms.CharField(label="Operación:", widget=forms.Select(choices=lst_comando))
    capa_in = forms.CharField(label="Capa de entrada:", widget=forms.Select(choices=[]))
    #capa_out = forms.CharField(label="Capa de salida:", widget=forms.TextInput())
    formato = forms.CharField(label="Formato:", widget=forms.Select(choices=lst_tipo,))
    setnull = forms.CharField(label="Valor nulo:", widget=forms.TextInput())
    categoria = forms.CharField(label="Categoría:", widget=forms.TextInput())
    
    def __init__(self, *args, **kwargs):  
        self.mapset = kwargs.pop('mapset', None)
        self.location = kwargs.pop('location', None)
        self.sector = kwargs.pop('sector', None)     
        super(ComandosForm, self).__init__(*args, **kwargs)     
    
        bd = []
        bd_sector = []
        
        sector = "BD cartográfica " + str(self.sector).lower()
        lst_capa = [(sector, (bd_sector)) , ("BD cartográfica general", (bd))  ]
        
        gsh.grass_init(self.location)
        rast = gsh.g_list('rast')        
        rast.sort()

        for r in rast:            
            bd.append(("r" + r, r))

        gsh.grass_init(self.location,self.mapset)
        rast = gsh.g_list('rast',permanent=False)        
        rast.sort()

        for r in rast:
            if r[0] != 'f':            
                bd_sector.append(("r" + r, r))
            
               
        self.fields['formato'].widget.attrs.update({'style': 'display: none'})
        self.fields['setnull'].widget.attrs.update({'style': 'display: none'})
        self.fields['categoria'].widget.attrs.update({'style': 'display: none'})
        self.fields['capa_in'].widget = forms.Select(choices=lst_capa)
                                                 


"""
    Select capas
"""

class BdCartografica(forms.Form):
    cartografica = forms.CharField(label="", widget=forms.Select(choices=[]))
    
    def __init__(self, *args, **kwargs):   
        self.location = kwargs.pop('location', None)     
        super(BdCartografica, self).__init__(*args, **kwargs)
        
        permanent = U.getMapSetPermanent(self.location)
            
        self.fields['cartografica'].widget = forms.Select(choices=permanent)
        self.fields['cartografica'].widget.attrs.update({'multiple':'multiple', 'class':'lst_cartografica'})


class MapaSector(forms.Form):
    mapa_sector = forms.CharField(label="", widget=forms.Select(choices=[]))
    
    def __init__(self, *args, **kwargs):  
        self.mapset = kwargs.pop('mapset', None)
        self.location = kwargs.pop('location', None)
        self.names_avoid = kwargs.pop('names_avoid', None)              
        super(MapaSector, self).__init__(*args, **kwargs)
        
        capa = U.getMapsetSector(self.location, self.mapset,self.names_avoid) 
        
        self.fields['mapa_sector'].widget = forms.Select(choices=capa)        
        self.fields['mapa_sector'].widget.attrs.update({'multiple':'multiple', 'class':'lst_cartografica'})


class MapaValor(forms.Form):
    mapa_valor = forms.CharField(label="", widget=forms.Select(choices=[]))
    
    def __init__(self, *args, **kwargs):
        self.id_ups = kwargs.pop('id_ups', None)
        super(MapaValor, self).__init__(*args, **kwargs)
                
        if self.id_ups > 0:
            capa = q.getMapaValor(self.id_ups)            
        else:
            capa = ()
        
        self.fields['mapa_valor'].widget = forms.Select(choices=capa)
        self.fields['mapa_valor'].widget.attrs.update({'multiple':'multiple', 'class':'lst_cartografica'})


class MapaAptitud(forms.Form):
    mapa_aptitud = forms.CharField(label="", widget=forms.Select(choices=[]))
    
    def __init__(self, *args, **kwargs):
        self.id_ups = kwargs.pop('id_ups', None)
        super(MapaAptitud, self).__init__(*args, **kwargs)
                
        if self.id_ups > 0:
            capa = q.getMapaAptitud(self.id_ups)            
        else:
            capa = ()
        
        self.fields['mapa_aptitud'].widget = forms.Select(choices=capa)
        self.fields['mapa_aptitud'].widget.attrs.update({'multiple':'multiple', 'class':'lst_cartografica'})
    
    
class MapaAptitudAdmin(forms.Form):
    mapa_aptitud = forms.CharField(label="", widget=forms.Select(choices=[]))    
    def __init__(self, *args, **kwargs):        
        self.id_ups = kwargs.pop('id_ups', None)
        self.id = kwargs.pop('id', None)        
        super(MapaAptitudAdmin, self).__init__(*args, **kwargs)                
        if self.id_ups > 0:
            capa = q.getMapaAptitudAdmin(self.id_ups)            
        else:
            capa = ()        
        self.fields['mapa_aptitud'].widget = forms.Select(choices=capa)
        self.fields['mapa_aptitud'].widget.attrs.update({'multiple':'multiple', 'class':'lst_cartografica_admin', 'id':self.id})
        
class MapaGrupoAdmin(forms.Form):
    mapa_aptitud = forms.CharField(label="", widget=forms.Select(choices=[]))    
    def __init__(self, *args, **kwargs):        
        self.id_ups = kwargs.pop('id_ups', None)
        self.id = kwargs.pop('id', None)        
        super(MapaGrupoAdmin, self).__init__(*args, **kwargs)  
        if self.id_ups > 0:
            #mapt = q.getMapa_Grupo_Aptitud();
            #capa = [(m.id,m.nombre) for m in mapt]
             mapt=None
             capa =None           
        else:
            capa = ()   
        self.fields['mapa_aptitud'].widget = forms.Select(choices=capa)
        self.fields['mapa_aptitud'].widget.attrs.update({'multiple':'multiple', 'class':'lst_cartografica_admin', 'id':self.id})
                