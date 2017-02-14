from django.conf.urls.defaults import *
from django.conf import settings
from django.contrib.auth.views import login

# Uncomment the next two lines to enable the admin:
#from django.contrib import admin
#admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^ecologia/', include('ecologia.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    #(r'^admin/', include(admin.site.urls)),
)

urlpatterns += patterns('django.views.static',
    # recurso web site_media,    
    (r'^site_media/(?P<path>.*)$', 'serve', {'document_root': settings.MEDIA_ROOT}),
)

urlpatterns += patterns('menu.views',
    # login
    (r'^ecologia/$','login'),
    (r'^ecologia$', 'login'),
    (r'^ecologia/login/$', 'login'),
    # logout
    (r'^ecologia/logout/$', 'logout'),
    #menu
    (r'^ecologia/menu/$', 'menu'),
    
    #redireccionar
    #(r'^.*',login),    
)

urlpatterns += patterns('programa.views',
    (r'^ecologia/programa/$', 'programa'),
    (r'^ecologia/seleccionprograma/$', 'get_programa_por_rol'),
    
    #ajax
    (r'^ecologia/get/programa/$', 'get_programa'),
    (r'^ecologia/get/operador/sector/$', 'get_operador_sector'),
        
    #ajax_form
    (r'^ecologia/set/asignar/$', 'set_asignar_sector_operador'),
    
)
urlpatterns += patterns('administracion.views',    
    (r'^ecologia/administracion/$', 'administracion'),
    (r'^ecologia/getuser/$', 'getUser'),
    (r'^ecologia/updateuser/$', 'updateUser'),    
    (r'^ecologia/exportexcel_programs/$', 'exportExcelPrograms'),
    
    
)
urlpatterns += patterns('preparacion_proceso.views',    
    (r'^ecologia/preparacion/$', 'preparacion'),    
    (r'^ecologia/sectores/$', 'sectores'),
    (r'^ecologia/operador_sector/$', 'get_operador_sector'),
    (r'^ecologia/asociar_operador_sector/$', 'asociar_operador_sector'),
    (r'^ecologia/preparar_sig/$', 'preparar_sig'),
    (r'^ecologia/exp_imp_capa/$', 'exportar_importar_capa'),
    (r'^ecologia/imp_exist_capa/$', 'existe_nombre_capa_importar'),
    (r'^ecologia/borrar_sector/$', 'borrar_sector'),
)

urlpatterns += patterns('ordenamiento.views',
                           
                        
    (r'^ecologia/grupos/$', 'grupos'),
    
    #ordenamiento
    (r'^ecologia/ordenamiento/$', 'ordenamiento'),
    
    
    #no programas
    (r'^ecologia/no_programa/$', 'no_programa'),
    
    (r'^ecologia/seguimiento_operadores/$', 'seguimiento_operadores'),
    (r'^ecologia/activacion_operador/$', 'activacion_operador'),
    (r'^ecologia/getfdiscretas/$', 'getfdiscretas'),
    (r'^ecologia/generafdiscreta/$', 'grass_fun_discreta'),
    
    
    
    #ajax
    (r'^ecolgoia/select/subsector/$', 'select_subsector'),
    
    (r'^ecologia/actividad/atributos/$', 'get_attrpeso_from_activity'),    
    
    (r'^ecolgoia/generate/aptitudegroups/$', 'generate_aptitude_groups'),
    
    (r'^ecolgoia/get_nodes/$', 'get_nodes'),
    
    (r'^ecolgoia/create_fisrt_node/$', 'generate_first_node'),
    
    (r'^ecolgoia/change_cut/$', 'change_cut'),
    
    (r'^ecolgoia/get_residuals/$', 'get_residuals'),
    
    (r'^ecolgoia/eliminate_nodes/$', 'eliminate_nodes'),
    
    (r'^ecologia/delcapa/$', 'grass_del_capa'),
    
    (r'^ecologia/export_averages/$', 'export_averages'),    
    
    (r'^ecologia/export_residuals/$', 'export_residuals'),
    
    (r'^grass/mapa/grupos/$', 'grass_mapa_grupos'),
    
    (r'^grass/mapa/grupos_img/$', 'show_group_image'),
    
    (r'^ecolgoia/check_maps_status/$', 'check_changes'),
    
    (r'^ecolgoia/eliminate_all/$', 'eliminate_all'),
    
    #ajax_form
    (r'^ecologia/set/actividad/$','form_actividad'),

    #ajax GRASS syntax 
    (r'^grass/syntax/$', 'grass_syntax'),
    
    #ajax GRASS        
    (r'^grass/permanent/$', 'grass_permanent'),
    (r'^grass/mapset/$', 'grass_mapset'),
    
    (r'^grass/mapset/valor/$', 'grass_mapset_valor'),
    (r'^grass/mapset/aptitud/$', 'grass_mapset_aptitud'),    
    (r'^grass/mapa/grupo/$', 'grass_mapa_grupo'),
    (r'^grass/continua/$', 'grass_fun_continua'),
    (r'^grass/aptitud/$', 'grass_mapa_aptitud'),
    (r'^grass/cmd/$', 'grass_cmd'),
    
    (r'^grass/aptitud/aprobar/$', 'grass_aptitud_aprobar'),    
)


urlpatterns += patterns('rol.views',
    (r'^ecologia/rol/$', 'rol'),
)

urlpatterns += patterns('exportar_importar.views',
    (r'^ecologia/exportar_importar/$', 'exportar_importar'),
)

urlpatterns += patterns('registro_historico.views',
    (r'^ecologia/registro_historico/$', 'registro_historico'),
)

