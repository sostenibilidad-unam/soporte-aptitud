from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template.context import RequestContext
import ordenamiento.querys as q
from lib.D import ROL as R
from django.contrib.auth.models import User
from lib.U import getUsrRol, getUsr
from django.db.models.query_utils import Q
from lib.D import PERMISSION as P
from datetime import datetime, date
from registro_historico.forms import SearchMovementsFrom
from ordenamiento.models import Accion
from lib import journal


@login_required
def registro_historico(request):
      
    html = "app/registro_historico.html"
    rol = getUsrRol(request)
    grupo = getUsr(request).username    
    arg = {}
    
    if rol == R.ROOT:
        uusers = User.objects.filter(Q(user_permissions__codename=P.ROOT2) | Q(is_superuser=True))
    elif rol == R.ROOT2:            
        uusers = User.objects.filter(Q(user_permissions__codename=P.ADMIN) | Q(user_permissions__codename=P.SUPERVISOR))   
    elif rol == R.ADMIN:            
        uusers = User.objects.filter(Q(user_permissions__codename=P.OPERADOR) & Q(groups__name=grupo))
    
    
    my_user = journal.getUserFromRequest(request)
    users = []
    users.append(my_user)
    for u in uusers:
        users.append(u)
    
        
    actions = Accion.objects.all()    
    
    if request.method == 'POST':
        user_selected = request.POST['user']
        accion_selected = request.POST['accion']
        
        from_selected = request.POST['fecha_desde']
        if from_selected != '':            
            from_selected = from_selected.split('-')
            if len(from_selected)==3:                            
                from_date = date(int(from_selected[0]),int(from_selected[1]),int(from_selected[2]))
            else:
                from_date = None
        else:
            from_date = None
        to_selected = request.POST['fecha_hasta']
        if to_selected != '':
            to_selected = to_selected.split('-')
            if len(to_selected)==3:
                to_date = date(int(to_selected[0]),int(to_selected[1]),int(to_selected[2]))
            else:
                to_date = None
        else:
            to_date = None    
                        
        if user_selected == '0':
            user_selected = [u.id for u in users]            
        if accion_selected == '0':
            accion_selected = None
              
        movements = q.getMovements(user_selected, accion_selected, from_date, to_date)
    else:
        movements = None                    
    
    user_data = []
    user_data.append(('0','Todos'))        
    for u in users:
        user_data.append((u.id,u.username))
    actions_data = []
    actions_data.append(('0','Todos'))
    for a in actions:
        actions_data.append((a.id, a.descripcion))
                        
    search_form = SearchMovementsFrom(usuarios=user_data, acciones=actions_data)
        
    arg["movements"] = movements
    arg["search_form"] = search_form
    
    return render_to_response(html, arg, context_instance=RequestContext(request))
