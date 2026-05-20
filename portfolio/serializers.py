from rest_framework import serializers
import cloudinary.utils
from .models import (
    Profile,
    Education,
    Certificate,
    Profession,
    TechStack,
    Project,
    SocialLink,
    Resume,
    Service,
    Testimonial,
    ContactMessage,
)


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = '__all__'
        read_only_fields = ['user']

class CertificateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Certificate
        fields = '__all__'
        read_only_fields = ['user']

class ProfessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profession
        fields = '__all__'
        read_only_fields = ['user']

class TechStackSerializer(serializers.ModelSerializer):
    class Meta:
        model = TechStack
        fields = '__all__'

class ProjectSerializer(serializers.ModelSerializer):
    technologies = TechStackSerializer(many=True, read_only=True)
    tech_stack_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=TechStack.objects.all(), source='technologies'
    )

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['user']

class SocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialLink
        fields = '__all__'
        read_only_fields = ['user']

class ResumeSerializer(serializers.ModelSerializer):
    file_url = serializers.SerializerMethodField()
    download_url = serializers.SerializerMethodField()

    class Meta:
        model = Resume
        fields = ['id', 'user', 'resume', 'file_url', 'download_url']
        read_only_fields = ['user']

    def get_file_url(self, obj):
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
        fields = '__all__'
        read_only_fields = ['user']

class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = '__all__'
        read_only_fields = ['user']

class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = '__all__'
        read_only_fields = ['user', 'created_at']


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
