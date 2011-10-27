from django.contrib import admin
from openletsweb.models import * 


admin.site.register(Person)
admin.site.register(Balance)
admin.site.register(Transaction)
admin.site.register(Currency)
admin.site.register(Resolution)
admin.site.register(ExchangeRate)
