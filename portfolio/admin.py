from django.contrib import admin
from .models import *

admin.site.register(CustomUser)
admin.site.register(Profile)
admin.site.register(Education)
admin.site.register(Certificate)
admin.site.register(Internship)
admin.site.register(Profession)

@admin.register(TechStack)
class TechStackAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

admin.site.register(Project)
admin.site.register(SocialLink)
admin.site.register(Resume)
