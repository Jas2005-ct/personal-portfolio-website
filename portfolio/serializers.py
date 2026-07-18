from rest_framework import serializers
import cloudinary.utils
from .models import (
    Profile,
    Education,
    Certificate,
    Profession,
    TechStack,
    Tech_Section,
    Project,
    SocialLink,
    Resume,
    Service,
    Testimonial,
    ContactMessage,
)


class Tech_SectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tech_Section
        fields = ['id', 'name', 'slug']

class TechStackSerializer(serializers.ModelSerializer):
    section_name = serializers.CharField(source='section.name', read_only=True)
    section_details = Tech_SectionSerializer(source='section', read_only=True)
    
    class Meta:
        model = TechStack
        fields = ['id', 'name', 'icon', 'section', 'section_name', 'section_details']

class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = [
            'id', 'course', 'institution', 'field_of_study', 'location', 'grade',
            'description', 'course_duration', 'start_year', 'end_year',
        ]
        read_only_fields = ['user']

class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = ['id', 'course', 'platform', 'image']
        read_only_fields = ['user']

class ProfessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profession
        fields = [
            'id', 'experience', 'company', 'role', 'location', 'description',
            'duration', 'start_year', 'end_year',
        ]
        read_only_fields = ['user']

class ProjectSerializer(serializers.ModelSerializer):
    technologies = TechStackSerializer(many=True, read_only=True)
    tech_stack_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=TechStack.objects.all(), source='technologies'
    )

    class Meta:
        model = Project
        fields = [
            'id', 'title', 'image', 'description', 'motive', 'problem_statement',
            'technologies', 'tech_stack_ids', 'github_link', 'live_demo',
            'impact', 'architecture_notes',
        ]
        read_only_fields = ['user']

class SocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialLink
        fields = ['id', 'github', 'linkedin', 'instagram', 'twitter', 'facebook']
        read_only_fields = ['user']

class ResumeSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = Resume
        fields = ['id', 'resume', 'file_url', 'download_url']
        read_only_fields = ['user']

    def get_file_url(self, obj):
        if not obj.resume:
            return None
        return obj.resume.url

    def get_download_url(self, obj):
        if not obj.resume:
            return None
        try:
            public_id = getattr(obj.resume, 'public_id', obj.resume.name)
            resource_type = getattr(obj.resume, 'resource_type', 'image') 
            
            url, options = cloudinary.utils.cloudinary_url(
                public_id,
                resource_type=resource_type,
                flags="attachment"
            )
            return url
        except Exception:
            return obj.resume.url

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ['id', 'title', 'description', 'icon']
        read_only_fields = ['user']

class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = ['id', 'name', 'role', 'company', 'quote', 'image']
        read_only_fields = ['user']

class ContactMessageSerializer(serializers.ModelSerializer):
    # Honeypot field - bots will fill this, humans won't see it
    website = serializers.CharField(required=False, allow_blank=True, write_only=True, default='')

    class Meta:
        model = ContactMessage
        fields = ['id', 'sender_name', 'sender_email', 'subject', 'message', 'created_at', 'website']
        read_only_fields = ['user', 'created_at']

    def validate_website(self, value):
        """Honeypot validation - if filled, it's likely a bot"""
        if value:
            raise serializers.ValidationError("Spam detected.")
        return value

    def validate_sender_email(self, value):
        """Basic email format validation"""
        if not value or '@' not in value:
            raise serializers.ValidationError("Invalid email format.")
        return value

    def create(self, validated_data):
        # Remove honeypot field before saving
        validated_data.pop('website', None)
        return super().create(validated_data)


class ProfileSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(source='user.email', read_only=True)
    technologies = TechStackSerializer(many=True, read_only=True)
    tech_stack_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=TechStack.objects.all(), source='technologies'
    )

    class Meta:
        model = Profile
        fields = '__all__'
        read_only_fields = ['user']
