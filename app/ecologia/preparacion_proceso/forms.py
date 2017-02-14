# -*- coding: utf-8 -*-
from django.utils.encoding import smart_str, smart_unicode
from django.forms.models import ModelForm
from cProfile import label
from django import forms
from ordenamiento.models import Sector, Programa, User_Programa_Sector
import lib.GrassShell as gsh
import ordenamiento.querys as q
import operator
import lib.U as U
import lib.D as D 
from django.contrib.auth.models import User

class SectorAltasForm(ModelForm):
    error_messages = {'invalid':"El campo no es valido", 'required':"El campo es requerido"}
    nombre = forms.CharField(label="*Sector:", required=True, error_messages=error_messages, max_length=30, widget=forms.TextInput())   
    prefijo_mapas = forms.CharField(label="*Prefijo mapas:", required=True, error_messages=error_messages, max_length=6, widget=forms.TextInput())    
    
          
    def __init__(self, *args, **kwargs):        
        self.programId = kwargs.pop('programId', None)
        super(SectorAltasForm, self).__init__(*args, **kwargs)
    class Meta:
        model = Sector
        fields = ('nombre','prefijo_mapas')
    """
    #Validar nombre en grass
    def isVarGrass(cad):
        if not cad:
            return False
        for s in cad:
            if not s.isalpha() and not s.isdigit() and not s == '_':
                return False
        return True   
    """ 
    def save(self,id_usr, programa):
        p = super(SectorAltasForm, self).save(commit=False)
        p.programa = programa
        p.save()
        return p
    def clean_prefijo_mapas(self):
        prefijo = self.cleaned_data['prefijo_mapas']
        isVarGrass = True
        for s in prefijo:
            if not s.isalpha() and not s.isdigit() and not s == '_':
                isVarGrass = False
        if not isVarGrass:
            raise forms.ValidationError("Los espacios, caracteres especiales no son permitidos.")
        return prefijo
    def clean_nombre(self):
        nombre = self.cleaned_data['nombre']
        isVarGrass = True
        for s in nombre:
            if not s.isalpha() and not s.isdigit() and not s == '_':
                isVarGrass = False
        if not isVarGrass:
            raise forms.ValidationError("Los espacios, caracteres especiales no son permitidos.")
        #Compara sin importar upper o lower case        
        programa = Programa.objects.get(pk=self.programId)
        sectorGuardado = Sector.objects.filter(nombre__iexact=nombre,programa=programa)
        if len(sectorGuardado)>0:
            raise forms.ValidationError("Sector ya existe")
        return smart_str(nombre)

class UsuariosSectorForm(forms.Form):
    operadores = forms.CharField(widget=forms.Select(choices=[]))
    sectores = forms.CharField(widget=forms.Select(choices=[]))
    
    def __init__(self, *args, **kwargs):   
        self.users = kwargs.pop('operadores', None)     
        self.sectors = kwargs.pop('sectores', None)
        super(UsuariosSectorForm, self).__init__(*args, **kwargs)
        opr = []
        sctrs = []
        for usr in self.users:
            opr.append([usr.id,usr.first_name + " " + usr.last_name])
        for sector in self.sectors:
            sctrs.append([sector.id,sector.nombre])
        self.fields['operadores'].widget = forms.Select(choices=opr, attrs={'style':'width:150px'})
        self.fields['sectores'].widget = forms.Select(choices=sctrs, attrs={'style':'width:150px'})

class PrepararSigForm(forms.Form):
    error_messages = {'invalid':"El campo no es valido", 'required':"El campo es requerido"}
    descripcion = forms.CharField(label="*Descripción:", required=True, error_messages=error_messages,widget=forms.Textarea)     
       
    def __init__(self, *args, **kwargs): 
        self.desc = kwargs.pop('descripcion', None)  
        super(PrepararSigForm, self).__init__(*args, **kwargs)
        error_messages = {'invalid':"El campo no es valido", 'required':"El campo es requerido"}
        self.fields['descripcion'] = forms.CharField(label="*Descripción:",error_messages=error_messages,widget=forms.Textarea(),required=True, initial=self.desc)
        #self.fields['descripcion'].widget = forms.Textarea(render_value=self.desc)
        
class ImportarCapaForm(forms.Form):
    error_messages = {'invalid':"El campo no es valido", 'required':"El campo es requerido"}
    
    nombre_capa = forms.CharField(label="Nombre de la capa nueva", max_length=50,required=True,error_messages=error_messages)
    capa  = forms.FileField(label="Capa a importar",required=True,error_messages=error_messages)
    
    
    def __init__(self, *args, **kwargs):
        super(ImportarCapaForm, self).__init__(*args, **kwargs)  
    """    
    def clean_nombre_capa(self):
        actividad = self.cleaned_data["actividad"]
        return nombre_capa
    """
    
class ExportarCapaForm(forms.Form):
    
    error_messages = {'invalid':"El campo no es valido", 'required':"El campo es requerido"}    
    capa_exportar = forms.CharField(label="Capa a exportar", widget=forms.Select(choices=[]),error_messages=error_messages,required=True)
    
    def __init__(self, *args, **kwargs):
        self.programa_id = kwargs.pop('programa_id', None) 
        self.label_capa_exportar = kwargs.pop('label_capa_exportar', None)
        super(ExportarCapaForm, self).__init__(*args, **kwargs)  
        
        #mapset = q.getMapset(self.programa_id)
        
        location = q.getLocationAdmin(self.programa_id)
        
        
        bd = []
        #lst_capa = [(sector, (bd_sector)) , ("BD cartográfica general", (bd))  ]
        lst_capa = [("",""),("BD cartográfica general", (bd))  ]
        # Maps del permanent
        gsh.grass_init(location)
        rast = gsh.g_list('rast')        
        rast.sort()
        #Ahora buscamos los mapas de los sectore
        programa = Programa.objects.get(pk=self.programa_id)
        programa_sectores = User_Programa_Sector.objects.filter(programa=programa)
        if len(programa_sectores)>0:
            for usector in programa_sectores:
                mapset_sec = q.getMapset(usector.id) 
                gsh.grass_init(location,mapset_sec)
                rast_sec = gsh.g_list('rast',permanent=False)        
                rast_sec.sort()
                bd_sector = []
                for r in rast_sec:            
                    bd_sector.append((mapset_sec + "**" +  r, r))
                    #bd_sector.append(("r" + r, r))
                lst_capa.append((usector.sector.nombre,bd_sector))
                
        #Agregando mapas del admin        
        mapset_admin = q.getMapsetAdmin(self.programa_id).name        
        gsh.grass_init(location,mapset_admin)
        rast_admin = gsh.g_list('rast',permanent=False)
        if "grupos" in rast_admin:
            bd_admin = []
            bd_admin.append((mapset_admin + "**" +  "grupos", "grupos"))
            lst_capa.append(("Admin",bd_admin))
        
        """    
        rast_admin.sort()
        bd_admin = []        
        for r in rast_admin:            
            bd_admin.append((mapset_admin + "**" +  r, r))        
        lst_capa.append(("Admin",bd_admin))
        """
        
        for r in rast:            
            bd.append(( "*PER*" +  r, r))
            #bd.append(("r" + r, r))
        self.fields['capa_exportar'].widget = forms.Select(choices=lst_capa)
        if self.label_capa_exportar != None:    
            self.fields['capa_exportar'].label = self.label_capa_exportar
        
         

class DiscreteFunctionForm(forms.Form):
    
    error_messages = {'invalid':"El campo no es valido", 'required':"El campo es requerido"}    
    capa_exportar = forms.CharField(label="Capa a exportar", widget=forms.Select(choices=[]),error_messages=error_messages,required=True)
    
    def __init__(self, *args, **kwargs):
        self.programa_id = kwargs.pop('programa_id', None) 
        self.ups = kwargs.pop('ups', None)
        self.label_capa_exportar = kwargs.pop('label_capa_exportar', None)
        
        super(DiscreteFunctionForm, self).__init__(*args, **kwargs)  
                
        location = q.getLocationProgram(self.programa_id)
        
        bd = []        
        #lst_capa = [("",""),("BD cartográfica general", (bd))  ]
        lst_capa = []
        
        
        
        #Ahora buscamos los mapas de los sectore        
        programa = Programa.objects.get(pk=self.programa_id)
        programa_sectores = self.ups
        
        
        if len(programa_sectores)>0:
            for usector in programa_sectores:
                mapset_sec = q.getMapset(usector.id) 
                gsh.grass_init(location,mapset_sec)
                rast_sec = gsh.g_list('rast',permanent=False)        
                rast_sec.sort()
                bd_sector = []
                for r in rast_sec:            
                    bd_sector.append((mapset_sec + "**" +  r, r))                    
                lst_capa.append((usector.sector.nombre,bd_sector))
        
        lst_capa.append(("BD cartográfica general", bd))        
        
        # Maps del permanent
        gsh.grass_init(location)
        rast = gsh.g_list('rast')        
        rast.sort()
                

        for r in rast:            
            bd.append(( "*PER*" +  r, r))
            
        self.fields['capa_exportar'].widget = forms.Select(choices=lst_capa)
        if self.label_capa_exportar != None:    
            self.fields['capa_exportar'].label = self.label_capa_exportar
        
               