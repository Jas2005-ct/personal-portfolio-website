from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'profile', views.ProfileViewSet)
router.register(r'education', views.EducationViewSet)
router.register(r'certificates', views.CertificateViewSet)
router.register(r'internships', views.InternshipViewSet)
router.register(r'professions', views.ProfessionViewSet)
router.register(r'skills', views.UserSkillViewSet)
router.register(r'skill-master', views.SkillMasterViewSet)
router.register(r'projects', views.ProjectViewSet)
router.register(r'social-links', views.SocialLinkViewSet)
router.register(r'resume', views.ResumeViewSet)
router.register(r'services', views.ServiceViewSet)
router.register(r'testimonials', views.TestimonialViewSet)
router.register(r'contact', views.ContactMessageViewSet)
router.register(r'technologies', views.TechnologyViewSet)

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('api/', include(router.urls)),
    path('api/portfolio-data/', views.PortfolioDataView.as_view(), name='portfolio-data'),
]
