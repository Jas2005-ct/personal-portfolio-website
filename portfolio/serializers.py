from rest_framework import serializers
import cloudinary.utils # Import cloudinary utils
from .models import (CustomUser, 
                    Profile, 
                    Education, 
                    Certificate, 
                    Internship,     
                    Profession, 
                    SkillMaster, 
                    UserSkill, 
                    Project, 
                    SocialLink, 
                    Resume, 
                    Service, 
                    Testimonial, 
                    ContactMessage, 
                    Technology)


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

class InternshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Internship
        fields = '__all__'
        read_only_fields = ['user']

class ProfessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profession
        fields = '__all__'
        read_only_fields = ['user']

class SkillMasterSerializer(serializers.ModelSerializer):
    class Meta:
        model = SkillMaster
        fields = '__all__'

class UserSkillSerializer(serializers.ModelSerializer):
    skill_details = SkillMasterSerializer(source='skill', read_only=True)
    
    class Meta:
        model = UserSkill
        fields = ['id', 'user', 'skill', 'skill_details', 'level', 'order']
        read_only_fields = ['user']

class TechnologySerializer(serializers.ModelSerializer):
    class Meta:
        model = Technology
        fields = '__all__'

class ProjectSerializer(serializers.ModelSerializer):
    # tech_stack = serializers.SerializerMethodField() # Removed to allow legacy model field
    technologies = TechnologySerializer(many=True, read_only=True)
    technology_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=Technology.objects.all(), source='technologies'
    )

    class Meta:
        model = Project
        fields = '__all__'
        read_only_fields = ['user']

    # def get_tech_stack(self, obj):
    #     return ", ".join([tech.name for tech in obj.technologies.all()])

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
        # Generate a proper download URL with attachment flag
        if not obj.resume:
            return None
        try:
            # Use public_id if available, otherwise try name
            public_id = getattr(obj.resume, 'public_id', obj.resume.name)
            # Ensure resource_type is handled (default to 'auto' or 'image' if not found)
            resource_type = getattr(obj.resume, 'resource_type', 'image') 
            
            url, options = cloudinary.utils.cloudinary_url(
                public_id,
                resource_type=resource_type,
                flags="attachment"
            )
            return url
        except Exception as e:
            # Fallback
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
    technologies = TechnologySerializer(many=True, read_only=True)
    technology_ids = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True, queryset=Technology.objects.all(), source='technologies'
    )

    class Meta:
        model = Profile
        fields = '__all__'
        read_only_fields = ['user']
