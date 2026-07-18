from django.contrib import admin
from .models import *
from django.utils.html import format_html

admin.site.register(CustomUser)
admin.site.register(Profile)
admin.site.register(Education)
admin.site.register(Certificate)
admin.site.register(Profession)
admin.site.register(Tech_Section)

@admin.register(TechStack)
class TechStackAdmin(admin.ModelAdmin):
    list_display = ('name', 'section', 'icon_preview', 'id')
    list_filter = ('section',)
    search_fields = ('name',)
    readonly_fields = ('icon_preview',)

    @admin.display(description='Icon')
    def icon_preview(self, obj):
        if obj.icon:
            return format_html('<img src="{}" alt="{}" style="height:48px;width:48px;object-fit:contain;border-radius:8px;border:1px solid #ddd;" />', obj.icon.url, obj.name)
        return format_html('<span style="color:#999;">No icon</span>')

admin.site.register(Project)
admin.site.register(SocialLink)
admin.site.register(Resume)
admin.site.register(Service)
admin.site.register(Testimonial)
admin.site.register(ContactMessage)
