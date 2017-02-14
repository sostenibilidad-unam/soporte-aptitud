# -*- coding: utf-8 -*-

from django.contrib.auth.models import User, Permission
from django.db import models, models



class Programa (models.Model):
    nombre = models.CharField(max_length=150,)
    location = models.CharField(max_length=50)
    modalidad = models.CharField(max_length=50)
    fecha_inicio = models.DateField() 
    responsable_autoridad = models.CharField(max_length=150)
    responsable_instituto = models.CharField(max_length=150)    
    responsable_dgpairs = models.CharField(max_length=150)
    responsable_ine = models.CharField(max_length=150)
    descripcion = models.TextField(blank=True)


class Sector (models.Model):    
    nombre = models.CharField(max_length=150)
    prefijo_mapas = models.CharField(max_length=20)
    programa = models.ForeignKey(Programa)
    def __unicode__(self):
        return self.nombre
    

class User_Programa_Sector (models.Model):
    user = models.ForeignKey(User,related_name='user')
    programa = models.ForeignKey(Programa , related_name='programa') 
    sector = models.ForeignKey(Sector, related_name='sector')
    # 0 = False, 1 = True
    activo = models.IntegerField(null=False, default=1)


class Actividad(models.Model):
    actividad = models.CharField(max_length=100)    
    user_sector_programa = models.ForeignKey(User_Programa_Sector)


class Atributo(models.Model):
    atributo = models.CharField(max_length=100)
    peso = models.DecimalField(max_digits=3, decimal_places=2)
    actividad = models.ForeignKey(Actividad)


class Mapa_Valor(models.Model):
    nombre = models.CharField(max_length=150)
    version = models.IntegerField()    
    funcion = models.IntegerField()
    min_escala = models.FloatField()
    max_escala = models.FloatField()
    saturacion = models.FloatField(null=True)
    amplitud = models.FloatField(null=True)    
    x_max = models.FloatField(null=True)
    x_min = models.FloatField(null=True)
    a_valor = models.FloatField(null=True)
    b_valor = models.FloatField(null=True)
    c_valor = models.FloatField(null=True)
    atributo = models.ForeignKey(Atributo)

        
class Mapa_Aptitud (models.Model):
    nombre = models.CharField(max_length=50) 
    peso = models.FloatField(null=True)
    descripcion = models.TextField(null=True)
    estatus = models.CharField(max_length=40,null=True)
    user_sector_programa = models.ForeignKey(User_Programa_Sector)
   
    
class Mapa_Aptitud_Mapa_Valor(models.Model):
    mapa_aptitud = models.ForeignKey(Mapa_Aptitud)
    mapa_valor = models.ForeignKey(Mapa_Valor)

"""

class Grupo_Mapa_Aptitud(models.Model):
    programa = models.ForeignKey(Programa)
 
    
class Grupo_Mapa_Aptitud_Mapa_Aptitud(models.Model):
    grupo_mapa_aptidu = models.ForeignKey(Grupo_Mapa_Aptitud)
    mapa_aptitud = models.ForeignKey(Mapa_Aptitud)

"""

class Mapset(models.Model):
    nombre = models.CharField(max_length=50)   
    user_programa_sector = models.ForeignKey(User_Programa_Sector)


class Accion(models.Model):
    descripcion = models.CharField(max_length=30)


class Bitacora(models.Model):    
    accion = models.ForeignKey(Accion)
    fecha = models.DateTimeField()    
    user = models.ForeignKey(User)
    detalles = models.CharField(max_length=100) 
    
    
class MapsetAdmin(models.Model):
    name = models.CharField(max_length=100)
    program = models.ForeignKey(Programa)  
    user = models.ForeignKey(User)
    
    
class MapaGruposAptitud(models.Model):
    programa = models.ForeignKey(Programa, null=True, on_delete=models.SET_NULL)    
    residuales = models.TextField(null=True)
    promedios = models.TextField(null=True)
    nodos = models.TextField(null=True)
    mapas = models.TextField(null=True)
    imagen = models.TextField(null=True)
    estado = models.IntegerField(null=True)

    
class NodoMapaGrupo(models.Model):        
    nodo_padre = models.ForeignKey("NodoMapaGrupo", null=True, on_delete=models.SET_NULL)
    nombre_primer_componente = models.CharField(max_length=200)
    nombre_primer_componente_reescalado = models.CharField(max_length=200)    
    es_final = models.BooleanField()      
    histogram_data = models.CharField(max_length=400)
    grupo = models.ForeignKey(MapaGruposAptitud, null=True, on_delete=models.SET_NULL)
    position = models.CharField(max_length=10)
    mascara = models.CharField(max_length=60, null=True)
    nombre = models.CharField(max_length=60, null=True)
    
  
class Corte(models.Model):
    imagen = models.TextField(blank=True)    
    nodo = models.ForeignKey(NodoMapaGrupo, related_name='padre', null=True, on_delete=models.SET_NULL)
    valor_corte = models.IntegerField()
    nombre_mascara_a = models.CharField(max_length=200)
    nombre_mascara_b = models.CharField(max_length=200)
    nombre_corte = models.CharField(max_length=200)    
    nodo_hijo_a = models.ForeignKey(NodoMapaGrupo, related_name='hijo_a', null=True, on_delete=models.SET_NULL)
    nodo_hijo_b = models.ForeignKey(NodoMapaGrupo, related_name='hijo_b', null=True, on_delete=models.SET_NULL)
    corte_ejecutado = models.BooleanField()
    selected = models.BooleanField()
    
    
    
class Rol(User):
    class Meta:
        permissions = (
            ('can_root', "Rol de super usuario (root)"),
            ('can_root2', "Rol de root2"),
            ('can_admin', "Rol de administrador"),
            ('can_supervisor', "Rol de supervisor"),
            ('can_operador', "Rol de operador"),
            ('can_operador_privilegios', "Rol de operador-grupo mapa aptitud"))

"""
class UserPermission(models.Model):
    user = models.ForeignKey(User)
    permission = models.ForeignKey(Permission)    
    class Meta:
        db_table = 'auth_user_user_permissions'
"""