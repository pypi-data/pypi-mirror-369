from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from .services import service_manager
from .apps import BysenserConfig


# Create your views here.

@login_required(login_url="/admin/")
def console_html(request):
    logs = service_manager.get_logs(count=200)
    return render(request, f'{BysenserConfig.name}/console.html', {'logs': logs})
