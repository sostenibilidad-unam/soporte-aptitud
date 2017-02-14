from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response
from django.template.context import RequestContext

@login_required
def exportar_importar(request):    
    html = "app/exportar_importar.html"
    arg = {}
    return render_to_response(html, arg, context_instance=RequestContext(request))

