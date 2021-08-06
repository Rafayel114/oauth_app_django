from django.contrib import admin
from accounts.models import CustomUser, CustomApplication, CustomGroup, UserGroup, CustomUserFields, Transaction, UserApp


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    model = CustomUser
    ordering = ['-id']
    search_fields = ['id', 'email',]



admin.site.register(CustomUserFields)
admin.site.register(CustomGroup)
admin.site.register(UserGroup)
admin.site.register(Transaction)
admin.site.register(UserApp)

from djangoredsmsapp.models import Sms
admin.site.register(Sms)

