from django.contrib import admin

# Register your models here.

from django.contrib import admin
from .models import Merchant, Payout

admin.site.register(Merchant)
admin.site.register(Payout)
