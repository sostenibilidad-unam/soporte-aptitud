from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models.query_utils import Q
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from lib.D import ROL as R
from lib.D import PERMISSION as P
from lib.U import getUsrRol, getUsr
from rol.forms import NewUserForm
from lib import journal


@login_required
def rol(request):
    html = "app/rol.html"
    rol = getUsrRol(request)
    grupo = getUsr(request).username
    arg = {}        
    if request.method == 'POST': 
        f = NewUserForm(request.POST, rol=rol)                        
        if f.is_valid():
            f.save(grupo)            
            arg['user_name'] = f.getUsr()        
            newUserName = f.cleaned_data['username'] 
            newUserRol = f.cleaned_data['rol']
            detalles = "usuario creado:" + newUserName + " rol:" + newUserRol                      
            journal.registerActionUserCreated(request, detalles)
            f = NewUserForm(rol=rol)                       
    else:
        f = NewUserForm(rol=rol)
        
    if rol == R.ROOT:
        u = User.objects.filter(Q(user_permissions__codename=P.ROOT2) | Q(is_superuser=True))
    elif rol == R.ROOT2:            
        u = User.objects.filter(Q(user_permissions__codename=P.ADMIN) | Q(user_permissions__codename=P.SUPERVISOR))   
    elif rol == R.ADMIN:            
        u = User.objects.filter(Q(user_permissions__codename=P.OPERADOR) & Q(groups__name=grupo))    
    u.order_by('username')        
    arg["frol"] = f
    arg["usr"] = u
    arg['rol'] = rol
    arg['ROL'] = R
    return render_to_response(html, arg, context_instance=RequestContext(request))



