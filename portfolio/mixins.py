from django.contrib.auth.mixins import UserPassesTestMixin, LoginRequiredMixin
from django.conf import settings
from django.shortcuts import redirect

class SuperAdminMixin(LoginRequiredMixin):
    """
    Mixin to ensure the user is the designated super admin or a superuser.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        
        # Check if user is a superuser
        if request.user.is_superuser:
            return super().dispatch(request, *args, **kwargs)
            
        # Check against the SUPER_ADMIN_EMAIL setting
        admin_email = getattr(settings, 'SUPER_ADMIN_EMAIL', None)
        if admin_email and request.user.email == admin_email:
            return super().dispatch(request, *args, **kwargs)
            
        # If neither, redirect to home
        return redirect('home')
