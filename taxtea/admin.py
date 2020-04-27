from django.contrib import admin

# Register your models here.
from taxtea.models import State, ZipCode

admin.site.register(State)
admin.site.register(ZipCode)
