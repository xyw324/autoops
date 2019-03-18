from django.contrib import admin
from . import models

admin.site.register(models.ConnectionInfo)
admin.site.register(models.VirtualServerInfo)
admin.site.register(models.HostGroup)
