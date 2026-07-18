import json

from django.shortcuts import render, redirect, get_object_or_404
from django.utils.safestring import mark_safe
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.views.generic import TemplateView
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import viewsets, permissions, pagination, status
from django.db.models import Count, Case, When, IntegerField
from django.db import connection
from .models import (
    Profile, Education, Certificate, Profession,
    TechStack, Tech_Section, Project, SocialLink, Resume, Service, Testimonial,
    ContactMessage, CustomUser
)
# pyright: ignore [missing-import]
from .serializers import (
    ProfileSerializer, EducationSerializer, CertificateSerializer, ProfessionSerializer,
    ProjectSerializer, SocialLinkSerializer, ResumeSerializer,
    ServiceSerializer, TestimonialSerializer, ContactMessageSerializer,
    TechStackSerializer, Tech_SectionSerializer
)
from .mixins import SuperAdminMixin
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm


class HealthCheckView(APIView):
    """Health check endpoint for Render/load balancer"""
    permission_classes = [permissions.AllowAny]
    authentication_classes = []

    def get(self, request):
        db_ok = True
        try:
            connection.ensure_connection()
        except Exception:
            db_ok = False
        
        status = 200 if db_ok else 503
        return Response({
            "status": "ok" if db_ok else "degraded",
            "database": "connected" if db_ok else "disconnected"
        }, status=status)


@method_decorator(cache_page(60 * 15), name='dispatch')
class HomeView(TemplateView):
    template_name = 'home.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = CustomUser.objects.filter(is_superuser=True).first()
        if not user:
            return context
        profile = Profile.objects.filter(user=user).prefetch_related('technologies__section').first()
        context['profile'] = profile
        context['json_ld'] = self._build_json_ld(profile, self.request)
        section_order = ['python', 'frontend', 'database', 'data-analytics']
        preserve_order = Case(
            *[When(section__slug=s, then=i) for i, s in enumerate(section_order)],
            output_field=IntegerField()
        )
        context['tech_stack'] = (
            TechStack
            .objects
            .select_related('section')
            .filter(section__slug__in=section_order, section__show_on_portfolio=True)
            .annotate(section_order=preserve_order)
            .order_by('section_order', 'name')
        )
        context['education'] = Education.objects.filter(user=user)
        context['certificates'] = Certificate.objects.filter(user=user)
        context['professions'] = Profession.objects.filter(user=user, experience='professional')
        context['internships'] = Profession.objects.filter(user=user, experience='internship')
        context['projects'] = Project.objects.filter(user=user).prefetch_related('technologies__section')
        context['social_links'] = SocialLink.objects.filter(user=user).first()
        context['resume'] = Resume.objects.filter(user=user).first()
        return context

    @staticmethod
    def _build_json_ld(profile, request):
        data = {
            "@context": "https://schema.org",
            "@type": "Person",
            "name": profile.name if profile else "",
            "jobTitle": profile.title if profile else "",
            "description": profile.bio if profile else "",
            "url": request.build_absolute_uri('/') if request else "",
        }
        # Serialize safely: escape characters that could break out of <script>.
        safe = json.dumps(data, ensure_ascii=False)
        safe = safe.replace('<', '\\u003c').replace('>', '\\u003e').replace('&', '\\u0026')
        return mark_safe(safe)

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
    def get(self, request):
        if request.user.is_authenticated:
            user = request.user
        else:
            user = CustomUser.objects.filter(is_superuser=True).first()

        if not user:
            return Response({"error": "No data found"}, status=404)

        profile = Profile.objects.filter(user=user).prefetch_related('technologies__section').first()
        social = SocialLink.objects.filter(user=user).first()
        resume_obj = Resume.objects.filter(user=user).first()

        section_order = ['python', 'frontend', 'database', 'data-analytics']
        preserve_order = Case(
            *[When(section__slug=s, then=i) for i, s in enumerate(section_order)],
            output_field=IntegerField()
        )

        data = {
            'profile': ProfileSerializer(profile).data if profile else None,
            'education': EducationSerializer(Education.objects.filter(user=user), many=True).data,
            'certificates': CertificateSerializer(Certificate.objects.filter(user=user), many=True).data,
            'professions': ProfessionSerializer(Profession.objects.filter(user=user), many=True).data,
            'tech_stack': TechStackSerializer(
                TechStack.objects.select_related('section')
                .filter(section__slug__in=section_order, section__show_on_portfolio=True)
                .annotate(section_order=preserve_order)
                .order_by('section_order', 'name'), many=True
            ).data,
            'profile_tech_stack': TechStackSerializer(
                profile.technologies.all(), many=True
            ).data if profile else [],
            'projects': ProjectSerializer(
                Project.objects.filter(user=user).prefetch_related('technologies__section'), many=True
            ).data,
            'social_links': SocialLinkSerializer(social).data if social else None,
            'resume': ResumeSerializer(resume_obj).data if resume_obj else None,
            'services': ServiceSerializer(Service.objects.filter(user=user), many=True).data,
            'testimonials': TestimonialSerializer(Testimonial.objects.filter(user=user), many=True).data,
        }
        return Response(data)

class BasePortfolioViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class ProfileViewSet(BasePortfolioViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def create(self, request, *args, **kwargs):
        # Profile is a OneToOne relation, so a second POST must update, not crash.
        profile, _created = Profile.objects.get_or_create(user=request.user)
        serializer = self.get_serializer(profile, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

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
    throttle_scope = 'contact'

    def get_permissions(self):
        if self.action == 'create':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return self.queryset.filter(user=self.request.user)
        return self.queryset.none()

    def perform_create(self, serializer):
        user = CustomUser.objects.filter(is_superuser=True).first()
        if not user:
            user = CustomUser.objects.first()
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
            section_id = int(section_id)
            section = Tech_Section.objects.get(id=section_id)
        except (ValueError, Tech_Section.DoesNotExist):
            return Response({'error': 'Invalid section'}, status=400)

        tech = TechStack.objects.filter(name=name, section=section).first()
        if tech:
            if icon:
                tech.icon = icon
            tech.save()
            serializer = self.get_serializer(tech)
            return Response(serializer.data, status=200)
        else:
            tech = TechStack(name=name, section=section)
            if icon:
                tech.icon = icon
            tech.save()
            serializer = self.get_serializer(tech)
            return Response(serializer.data, status=201)

class Tech_SectionViewSet(viewsets.ModelViewSet):
    queryset = Tech_Section.objects.all()
    serializer_class = Tech_SectionSerializer
    pagination_class = None

    def get_permissions(self):
        if self.request.method in permissions.SAFE_METHODS:
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]
