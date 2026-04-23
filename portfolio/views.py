from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, permissions
from .models import (
    Profile, Education, Certificate, Internship, Profession, 
    SkillMaster, UserSkill, Project, SocialLink, Resume, Service, Testimonial, 
    ContactMessage, Technology, CustomUser
)
from .serializers import (
    ProfileSerializer, EducationSerializer, CertificateSerializer, 
    InternshipSerializer, ProfessionSerializer, UserSkillSerializer, 
    ProjectSerializer, SocialLinkSerializer, ResumeSerializer,
    ServiceSerializer, TestimonialSerializer, ContactMessageSerializer,
    TechnologySerializer, SkillMasterSerializer
)
from .mixins import SuperAdminMixin
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm

class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch the first superuser's profile for public view
        user = CustomUser.objects.filter(is_superuser=True).first()
        if user:
            context['profile'] = Profile.objects.filter(user=user).first()
            context['education'] = Education.objects.filter(user=user).order_by('-start_year')
            context['certificates'] = Certificate.objects.filter(user=user)
            context['internships'] = Internship.objects.filter(user=user).order_by('-start_year')
            context['professions'] = Profession.objects.filter(user=user).order_by('-start_year')
            # Group skills by category for the frontend
            user_skills = UserSkill.objects.filter(user=user).select_related('skill').order_by('skill__category', 'order')
            grouped_skills = {}
            for us in user_skills:
                cat = us.skill.get_category_display()
                if cat not in grouped_skills:
                    grouped_skills[cat] = []
                grouped_skills[cat].append(us)
            context['grouped_skills'] = grouped_skills
            context['skills'] = user_skills  # Keep this for backward compatibility if template uses it
            context['projects'] = Project.objects.filter(user=user)
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
        context['internships'] = Internship.objects.filter(user=user)
        context['professions'] = Profession.objects.filter(user=user)
        context['skills'] = UserSkill.objects.filter(user=user)
        context['projects'] = Project.objects.filter(user=user)
        context['social_links'] = SocialLink.objects.filter(user=user).first()
        context['resume'] = Resume.objects.filter(user=user).first()
        context['services'] = Service.objects.filter(user=user)
        context['testimonials'] = Testimonial.objects.filter(user=user)
        context['tech_stack'] = Technology.objects.all()
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

        data = {
            'profile': ProfileSerializer(Profile.objects.filter(user=user).first()).data,
            'education': EducationSerializer(Education.objects.filter(user=user), many=True).data,
            'certificates': CertificateSerializer(Certificate.objects.filter(user=user), many=True).data,
            'internships': InternshipSerializer(Internship.objects.filter(user=user), many=True).data,
            'professions': ProfessionSerializer(Profession.objects.filter(user=user), many=True).data,
            'skills': UserSkillSerializer(UserSkill.objects.filter(user=user), many=True).data,
            'projects': ProjectSerializer(Project.objects.filter(user=user), many=True).data,
            'social_links': SocialLinkSerializer(SocialLink.objects.filter(user=user).first()).data,
            'resume': ResumeSerializer(Resume.objects.filter(user=user).first()).data,
            'services': ServiceSerializer(Service.objects.filter(user=user), many=True).data,
            'testimonials': TestimonialSerializer(Testimonial.objects.filter(user=user), many=True).data,
            'tech_stack': TechnologySerializer(Technology.objects.all(), many=True).data,
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

class InternshipViewSet(BasePortfolioViewSet):
    queryset = Internship.objects.all()
    serializer_class = InternshipSerializer

class ProfessionViewSet(BasePortfolioViewSet):
    queryset = Profession.objects.all()
    serializer_class = ProfessionSerializer

class UserSkillViewSet(BasePortfolioViewSet):
    queryset = UserSkill.objects.all()
    serializer_class = UserSkillSerializer

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
        # Assign to the first user for now, or handle dynamic user assignment if needed
        from .models import CustomUser
        user = CustomUser.objects.first()
        serializer.save(user=user)

class TechnologyViewSet(viewsets.ModelViewSet):
    queryset = Technology.objects.all()
    serializer_class = TechnologySerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        name = request.data.get('name')
        if name:
            technology, created = Technology.objects.get_or_create(name=name)
            serializer = self.get_serializer(technology)
            return Response(serializer.data)
        return Response({'error': 'Name is required'}, status=400)

class SkillMasterViewSet(viewsets.ModelViewSet):
    queryset = SkillMaster.objects.all()
    serializer_class = SkillMasterSerializer
    permission_classes = [permissions.IsAuthenticated]
