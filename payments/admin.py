from django.contrib import admin
from .models import Invoice

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('user', 'total', 'amount', 'payment_complete', 'invoice_code')
    search_fields = ('user__username', 'invoice_code')
