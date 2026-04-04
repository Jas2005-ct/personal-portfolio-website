from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.forms import AuthenticationForm
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, permissions
from .models import (
    Profile, Education, Certificate, Internship, Profession, Skill, 
    Project, SocialLink, Resume, Service, Testimonial, ContactMessage, Technology
)
from .serializers import (
    ProfileSerializer, EducationSerializer, CertificateSerializer, 
    InternshipSerializer, ProfessionSerializer, SkillSerializer, 
    ProjectSerializer, SocialLinkSerializer, ResumeSerializer,
    ServiceSerializer, TestimonialSerializer, ContactMessageSerializer,
    TechnologySerializer
)
from .forms import CustomUserCreationForm

def home(request):
    return render(request, 'home.html')

@user_passes_test(lambda u: u.is_superuser, login_url='login')
def dashboard(request):
    return render(request, 'dashboard.html')

# def register(request):
#     if request.method == 'POST':
#         form = CustomUserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request, user)
#             if user.is_superuser:
#                 return redirect('dashboard')
#             return redirect('home')
#     else:
#         form = CustomUserCreationForm()
#     return render(request, 'register.html', {'form': form})

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
    def get(self, request):
        # Prioritize logged-in user, otherwise fallback to the first user (for public view)
        if request.user.is_authenticated:
            user = request.user
        else:
            # Fallback to the first user found (or specific logic like is_superuser)
            from .models import CustomUser
            user = CustomUser.objects.first()

        if user:
            profile = Profile.objects.filter(user=user).first()
            education = Education.objects.filter(user=user)
            certificates = Certificate.objects.filter(user=user)
            internships = Internship.objects.filter(user=user)
            professions = Profession.objects.filter(user=user)
            skills = Skill.objects.filter(user=user)
            projects = Project.objects.filter(user=user)
            social_links = SocialLink.objects.filter(user=user).first()
            resume = Resume.objects.filter(user=user).first()
            services = Service.objects.filter(user=user)
            testimonials = Testimonial.objects.filter(user=user)
            # tech_stack is now part of profile.technologies
            tech_stack = profile.technologies.all() if profile else []
        else:
            profile = None
            education = []
            certificates = []
            internships = []
            professions = []
            skills = []
            projects = []
            social_links = None
            resume = None
            services = []
            testimonials = []
            tech_stack = []

        data = {
            'profile': ProfileSerializer(profile).data if profile else None,
            'education': EducationSerializer(education, many=True).data,
            'certificates': CertificateSerializer(certificates, many=True).data,
            'internships': InternshipSerializer(internships, many=True).data,
            'professions': ProfessionSerializer(professions, many=True).data,
            'skills': SkillSerializer(skills, many=True).data,
            'projects': ProjectSerializer(projects, many=True).data,
            'social_links': SocialLinkSerializer(social_links).data if social_links else None,
            'resume': ResumeSerializer(resume).data if resume else None,
            'services': ServiceSerializer(services, many=True).data,
            'testimonials': TestimonialSerializer(testimonials, many=True).data,
            'tech_stack': TechnologySerializer(tech_stack, many=True).data,
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

class SkillViewSet(BasePortfolioViewSet):
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer

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
