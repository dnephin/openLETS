from django.contrib import admin
from core.models import * 


admin.site.register(Person)
admin.site.register(PersonBalance)
admin.site.register(Balance)
admin.site.register(Transaction)
admin.site.register(TransactionRecord)
admin.site.register(Currency)
admin.site.register(Resolution)
admin.site.register(PersonResolution)
admin.site.register(ExchangeRate)
