# -*- coding: utf-8 -*-
from django import forms
from django.forms.models import ModelForm
from django.db.models import Q
from lib.D import ROL
from ordenamiento.models import Programa, Sector, User_Programa_Sector, \
    Mapset, MapsetAdmin, MapaGruposAptitud
import lib.GrassShell as gsh
import programa.querys as q
from datetime import date

class SeleccionaProgramaForm(ModelForm):
    programas = forms.CharField(label="*Procesos", widget=forms.Select(choices=[]))
    
    class Meta:
        model = Programa
        fields = ()
        
    def __init__(self, *args, **kwargs):
        self.rol = kwargs.pop('rol', None)
        self.user = kwargs.pop('user', None)
        self.userId = self.user.id
        super(SeleccionaProgramaForm, self).__init__(*args, **kwargs)  
        programas_combo = []
        if self.rol == ROL.ADMIN:                        
            programas = Programa.objects.filter(responsable_instituto=self.userId)            
            for programa in programas:                
                programas_combo.append([programa.id,programa.nombre])
        elif self.rol == ROL.OPERADOR:
            SI_ACTIVO = 1
            #Obtengo los Ids de los programas a los que el operador pertenece
            programas_ids_raw = User_Programa_Sector.objects.filter(user=self.user,activo=SI_ACTIVO).select_related("programa").values_list("programa").distinct()#.order_by("id");  
            programas_ids = []
            for programa_id in programas_ids_raw:
                programas_ids.append(programa_id[0])
            #Obtengo los objetos Programa a partir de los ids de los programas
            programas = Programa.objects.filter(id__in=programas_ids)    
            for programa in programas:                
                programas_combo.append([programa.id,programa.nombre])
        elif self.rol == ROL.SUPERVISOR:
            programas = Programa.objects.filter(Q(responsable_autoridad=self.userId) | Q(responsable_autoridad=self.userId) | Q(responsable_dgpairs=self.userId) | Q(responsable_ine=self.userId) )            
            for programa in programas:                
                programas_combo.append([programa.id,programa.nombre])
                
        self.fields['programas'].widget = forms.Select(choices=programas_combo)       
    
class ProgramaForm(ModelForm):

    error_messages = {'invalid':"El campo no es valido", 'required':"El campo es requerido"}
    
    nombre = forms.CharField(label="*Nombre del proceso OE:", error_messages=error_messages)
    fecha_inicio = forms.DateField(label="*Fecha de inicio:")#, error_messages=error_messages)    
    location = forms.CharField(label="*Location", error_messages=error_messages, widget=forms.Select(choices=[]))
    modalidad = forms.CharField(label="*Modalidad: regional/local/marino", error_messages=error_messages, widget=forms.Select(choices=[]))
    
    responsable_autoridad = forms.CharField(label="*Autoridad responsable del proceso", error_messages=error_messages, widget=forms.Select(choices=[]))
    responsable_instituto = forms.CharField(label="*Responsable del estudio técnico", error_messages=error_messages, widget=forms.Select(choices=[]))    
    responsable_dgpairs = forms.CharField(label="*Responsable en DGPAIRS", error_messages=error_messages, widget=forms.Select(choices=[]))
    responsable_ine = forms.CharField(label="Supervisor", error_messages=error_messages, required=False, widget=forms.Select(choices=[]))

    #sector = forms.CharField(error_messages=error_messages, widget=forms.CheckboxSelectMultiple(choices=Sector.objects.values_list()))
         
         
    def clean_fecha_inicio(self):
        f = self.cleaned_data["fecha_inicio"]
        
        hoy = date.today()
        fecha = date(f.year,f.month,f.day)
        
        if fecha < hoy:        
            raise forms.ValidationError("La fecha ya expiró")
        return f
         
    class Meta:
        model = Programa
        fields = ('nombre', 'location', 'modalidad','fecha_inicio', 'responsable_autoridad', 'responsable_instituto', 'responsable_dgpairs', 'responsable_ine')
        

        
    def __init__(self, *args, **kwargs):
        self.grupo = kwargs.pop('grupo', None)
        super(ProgramaForm, self).__init__(*args, **kwargs)
        
        modalidades = [
           ('regional', 'Regional'),
           ('local', 'Local'),
           ('marino', 'Marino'),
        ]

        location = []
        for l in gsh.getLocation():
            location.append((l, l))
          
        self.fields['modalidad'].widget = forms.Select(choices=modalidades)        
        self.fields['location'].widget = forms.Select(choices=location)
        self.fields['responsable_instituto'].widget = forms.Select(choices=[['','']] +q.get_all_rol(ROL.ADMIN))

        self.fields['responsable_autoridad'].widget = forms.Select(choices=[['','']] +q.get_supervisor(self.grupo))
        self.fields['responsable_dgpairs'].widget = forms.Select(choices=[['','']] +q.get_supervisor(self.grupo))        
        self.fields['responsable_ine'].widget = forms.Select(choices=[['','']] + q.get_supervisor(self.grupo))
        
        
    def save(self, id_usr, commit=True):
        p = super(ProgramaForm, self).save(commit=False)                
        #sector = self.cleaned_data['sector']
    
        responsable_id = int(p.responsable_instituto)
        
        
        
        if commit:
            p.save();
            program_id = p.id
            #for id in sector:
            #    if(id.isdigit()):
            #        s = User_Programa_Sector(user_id=id_usr, programa_id=p.id, sector_id=id)
            #        s.save()
            #        s = User_Programa_Sector(user_id=responsable_id, programa_id=p.id, sector_id=id)
            #        s.save()
                    
            #create mapset for admin            
            name = "admin_p_" + str(program_id) + "_admin_" + str(responsable_id)                        
            m = MapsetAdmin(name=name, program_id=program_id, user_id=responsable_id)
            m.save()
            grupos = MapaGruposAptitud(programa_id=program_id, residuales='', promedios='')
            grupos.save()                    
            gsh.create_mapset(m.name, m.program.location)
            
        return p           
        
        

class AsignarForm(forms.Form):
    
    programa = forms.CharField(required=True, widget=forms.HiddenInput())
    sector = forms.CharField(widget=forms.Select(choices=[]))
    operador = forms.CharField(widget=forms.RadioSelect(choices=[]))
         
    def __init__(self, *args, **kwargs):
        self.grupo = kwargs.pop('grupo', None)
        super(AsignarForm, self).__init__(*args, **kwargs)  
        
              
        self.fields["operador"].widget = forms.RadioSelect(choices=q.get_all_operador_and_operador_grupo(self.grupo))
            
    def save(self, id_admin, commit=True):
        if commit:
            id_programa = self.cleaned_data['programa']
            id_sector = self.cleaned_data['sector']
            id_operador = self.cleaned_data['operador']
            
            id_operador2 = 0
            
            us = User_Programa_Sector.objects.filter(programa=id_programa, sector=id_sector).exclude(user=id_admin)            
            for u in us:
                if u.user.has_perm(ROL.OPERADOR) and not u.user.is_superuser:           
                    id_operador2 = u.id
        
            #update 
            if id_operador2 != 0:
                u = User_Programa_Sector.objects.get(id=id_operador2)
                u.user_id = id_operador
                u.save()
                
            #insert
            else:
                us = User_Programa_Sector(user_id=id_operador, programa_id=id_programa, sector_id=id_sector)
                us.save();
                
                p = Programa.objects.get(id=id_programa)
                
                nombre = "sector" + str(us.id)
                m = Mapset(nombre=nombre, user_programa_sector_id=us.id)
                m.save()                    
                gsh.create_mapset(m.nombre, p.location)
                
            
 
        
        
        
        
"""
    Select programas
"""
class ProgramaSelect(forms.Form):
    programa = forms.CharField(label="", widget=forms.Select(choices=[]))
    
    def __init__(self, *args, **kwargs):       
        self.id_usr = kwargs.pop('id_usr', None)
        self.rol = kwargs.pop('rol', None)
        super(ProgramaSelect, self).__init__(*args, **kwargs)
        
        lst = []
        for p in Programa.objects.select_related('programa').filter(programa__user=self.id_usr).distinct('user_id'):
            lst.append((p.id, p.nombre))
        
        self.fields['programa'].widget = forms.Select(choices=lst)
        self.fields['programa'].widget.attrs.update({'multiple':'multiple', 'class':'lst_cartografica'})
        
        if self.rol == ROL.ADMIN:
            self.fields['programa'].widget.attrs['id'] = 'id_programa_admin'
            
        elif self.rol == ROL.ROOT2:
            self.fields['programa'].widget.attrs['id'] = 'id_programa_root2'
        
        

                
        
        
