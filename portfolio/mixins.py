from django.contrib.auth.mixins import UserPassesTestMixin
from django.conf import settings
from django.shortcuts import redirect

class SuperAdminMixin(UserPassesTestMixin):
    """
    Mixin to ensure the user is the designated super admin.
    """
    def test_func(self):
        if not self.request.user.is_authenticated:
            return False
            
        # Check against the SUPER_ADMIN_EMAIL setting
        super_admin_email = getattr(settings, 'SUPER_ADMIN_EMAIL', None)
        return self.request.user.email == super_admin_email

    def handle_no_permission(self):
        if not self.request.user.is_authenticated:
            return redirect('login')
        return redirect('home')
