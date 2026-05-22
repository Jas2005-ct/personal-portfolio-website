from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, permissions
from .models import (
    Profile, Education, Certificate, Profession,
    TechStack, Tech_Section, Project, SocialLink, Resume, Service, Testimonial,
    ContactMessage, CustomUser
)
from .serializers import (
    ProfileSerializer, EducationSerializer, CertificateSerializer, ProfessionSerializer,
    ProjectSerializer, SocialLinkSerializer, ResumeSerializer,
    ServiceSerializer, TestimonialSerializer, ContactMessageSerializer,
    TechStackSerializer, Tech_SectionSerializer
)
from .mixins import SuperAdminMixin
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm

class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = CustomUser.objects.filter(is_superuser=True).first()
        if user:
            profile = Profile.objects.filter(user=user).prefetch_related('technologies').first()
            context['profile'] = profile
            context['tech_stack'] = TechStack.objects.select_related('section').all()
            context['education'] = Education.objects.filter(user=user).order_by('-start_year')
            context['certificates'] = Certificate.objects.filter(user=user)
            context['professions'] = Profession.objects.filter(user=user).order_by('-start_year')
            context['projects'] = Project.objects.filter(user=user).prefetch_related('technologies')
            context['social_links'] = SocialLink.objects.filter(user=user).first()
            context['resume'] = Resume.objects.filter(user=user).first()
            context['services'] = Service.objects.filter(user=user)
            context['testimonials'] = Testimonial.objects.filter(user=user)
        return context

class DashboardView(SuperAdminMixin, TemplateView):
    template_name = 'dashboard.html'   

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context['profile'] = Profile.objects.filter(user=user).first()
        context['education'] = Education.objects.filter(user=user)
        context['certificates'] = Certificate.objects.filter(user=user)
        context['professions'] = Profession.objects.filter(user=user)
        context['projects'] = Project.objects.filter(user=user)
        context['social_links'] = SocialLink.objects.filter(user=user).first()
        context['resume'] = Resume.objects.filter(user=user).first()
        context['services'] = Service.objects.filter(user=user)
        context['testimonials'] = Testimonial.objects.filter(user=user)
        context['tech_stack'] = TechStack.objects.select_related('section').all()
        return context

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            if user.is_superuser:
                return redirect('dashboard')
            return redirect('home')
    else:
        form = AuthenticationForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('login')

class PortfolioDataView(APIView):
    """
    API endpoint that returns all portfolio data in JSON format.
    Used for AJAX loading if needed.
    """
    def get(self, request):
        if request.user.is_authenticated:
            user = request.user
        else:
            user = CustomUser.objects.filter(is_superuser=True).first()

        if not user:
            return Response({"error": "No data found"}, status=404)

        profile = Profile.objects.filter(user=user).prefetch_related('technologies').first()
        data = {
            'profile': ProfileSerializer(profile).data,
            'education': EducationSerializer(Education.objects.filter(user=user), many=True).data,
            'certificates': CertificateSerializer(Certificate.objects.filter(user=user), many=True).data,
            'professions': ProfessionSerializer(Profession.objects.filter(user=user), many=True).data,
            'tech_stack': TechStackSerializer(TechStack.objects.all(), many=True).data,
            'profile_tech_stack': TechStackSerializer(
                profile.technologies.all(), many=True
            ).data if profile else [],
            'projects': ProjectSerializer(Project.objects.filter(user=user), many=True).data,
            'social_links': SocialLinkSerializer(SocialLink.objects.filter(user=user).first()).data,
            'resume': ResumeSerializer(Resume.objects.filter(user=user).first()).data,
            'services': ServiceSerializer(Service.objects.filter(user=user), many=True).data,
            'testimonials': TestimonialSerializer(Testimonial.objects.filter(user=user), many=True).data,
        }
        return Response(data)

# Base ViewSet for user-specific data
class BasePortfolioViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ProfileViewSet(BasePortfolioViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

class EducationViewSet(BasePortfolioViewSet):
    queryset = Education.objects.all()
    serializer_class = EducationSerializer

class CertificateViewSet(BasePortfolioViewSet):
    queryset = Certificate.objects.all()
    serializer_class = CertificateSerializer


class ProfessionViewSet(BasePortfolioViewSet):
    queryset = Profession.objects.all()
    serializer_class = ProfessionSerializer

class ProjectViewSet(BasePortfolioViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

class SocialLinkViewSet(BasePortfolioViewSet):
    queryset = SocialLink.objects.all()
    serializer_class = SocialLinkSerializer

class ResumeViewSet(BasePortfolioViewSet):
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer

class ServiceViewSet(BasePortfolioViewSet):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer

class TestimonialViewSet(BasePortfolioViewSet):
    queryset = Testimonial.objects.all()
    serializer_class = TestimonialSerializer

class ContactMessageViewSet(viewsets.ModelViewSet):
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    
    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return self.queryset.filter(user=self.request.user)
        return self.queryset.none()
    
    def perform_create(self, serializer):
        from .models import CustomUser
        # Assign message to superuser (portfolio owner)
        user = CustomUser.objects.filter(is_superuser=True).first()
        if not user:
            user = CustomUser.objects.first()  # Fallback if no superuser exists
        serializer.save(user=user)

class TechStackViewSet(viewsets.ModelViewSet):
    queryset = TechStack.objects.all()
    serializer_class = TechStackSerializer

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        name = request.data.get('name')
        section_id = request.data.get('section')
        icon = request.FILES.get('icon')

        if not name or not section_id:
            return Response({'error': 'Name and section are required'}, status=400)

        try:
            section = Tech_Section.objects.get(id=section_id)
        except Tech_Section.DoesNotExist:
            return Response({'error': 'Invalid section'}, status=400)

        tech = TechStack.objects.filter(name=name).first()
        if not tech:
            tech = TechStack(name=name, section=section)
            if icon:
                tech.icon = icon
            tech.save()
        else:
            # Update if already exists
            if icon:
                tech.icon = icon
            if section:
                tech.section = section
            tech.save()
                
        serializer = self.get_serializer(tech)
        return Response(serializer.data)

class Tech_SectionViewSet(viewsets.ModelViewSet):
    queryset = Tech_Section.objects.all()
    serializer_class = Tech_SectionSerializer
    permission_classes = [permissions.AllowAny]
