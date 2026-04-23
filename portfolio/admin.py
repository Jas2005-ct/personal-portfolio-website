from django.contrib import admin
from .models import *

admin.site.register(CustomUser)
admin.site.register(Profile)
admin.site.register(Education)
admin.site.register(Certificate)
admin.site.register(Internship)
admin.site.register(Profession)
@admin.register(SkillMaster)
class SkillMasterAdmin(admin.ModelAdmin):
    list_display = ('name', 'category')
    list_filter = ('category',)
    search_fields = ('name',)
    ordering = ('category', 'name')

@admin.register(UserSkill)
class UserSkillAdmin(admin.ModelAdmin):
    list_display = ('user', 'skill', 'level', 'order')
    list_filter = ('level', 'skill__category')
    search_fields = ('user__email', 'skill__name')
    ordering = ('user', 'order')
admin.site.register(Project)
admin.site.register(SocialLink)
admin.site.register(Resume)
admin.site.register(Technology)