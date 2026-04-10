from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from cloudinary.models import CloudinaryField


class CustomManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class Technology(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    objects = CustomManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email

class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    title = models.CharField(max_length=100, help_text="e.g. Full Stack Developer", null=True, blank=True)
    bio = models.TextField(blank=True)
    profile_image = models.ImageField(upload_to='profile_images/', null=True, blank=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    technologies = models.ManyToManyField('Technology', blank=True)
    philosophy = models.TextField(blank=True, help_text="Your engineering mindset and development approach")

    def __str__(self):
        return self.name

class Education(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    course = models.CharField(max_length=100)
    institution = models.CharField(max_length=100)
    course_duration = models.CharField(max_length=100)
    start_year = models.IntegerField()
    end_year = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.course

class Certificate(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    course = models.CharField(max_length=100)
    platform = models.CharField(max_length=100)
    image = models.ImageField(upload_to='certificates/', null=True, blank=True)
    
    def __str__(self):
        return self.course

class Internship(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    company = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    start_year = models.IntegerField()
    end_year = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.company

class Profession(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    company = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    duration = models.CharField(max_length=100)
    start_year = models.IntegerField()
    end_year = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.company

class Skill(models.Model):
    level_choices = (
        ('Beginner', 'Beginner'),
        ('Intermediate', 'Intermediate'),
        ('Advanced', 'Advanced'),
    )

    category_choices = (
        ('Frontend', 'Frontend'),
        ('Backend', 'Backend'),
        ('DevOps', 'DevOps'),
        ('Tools', 'Tools'),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    skill = models.CharField(max_length=100)
    level = models.CharField(max_length=100, choices=level_choices)
    category = models.CharField(max_length=100, choices=category_choices, default='Backend')
    image = models.ImageField(upload_to='skills/', null=True, blank=True)
    
    def __str__(self):
        return self.skill

class Project(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    image = models.ImageField(upload_to='projects/', null=True, blank=True)
    description = models.TextField()
    motive = models.CharField(max_length=100)
    problem_statement = models.TextField()
    technologies = models.ManyToManyField(Technology, blank=True)
    tech_stack = models.CharField(max_length=200, help_text="Comma separated, e.g. Django, React", blank=True, null=True)
    github_link = models.URLField(null=True, blank=True)
    live_demo = models.URLField(null=True, blank=True)    
    impact = models.TextField(blank=True, help_text="Quantifiable results, e.g., 'Reduced load time by 30%'")
    architecture_notes = models.TextField(blank=True, help_text="Deep-dive into technical decisions and trade-offs")

    def __str__(self):
        return self.title

class SocialLink(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    github = models.URLField(null=True, blank=True)
    linkedin = models.URLField(null=True, blank=True)
    instagram = models.URLField(null=True, blank=True)
    twitter = models.URLField(null=True, blank=True)
    facebook = models.URLField(null=True, blank=True)

class Resume(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    resume = CloudinaryField('resume', resource_type='auto', folder='resume')

class Service(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, help_text="FontAwesome class, e.g. fas fa-code")

    def __str__(self):
        return self.title

class Testimonial(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    company = models.CharField(max_length=100, blank=True)
    quote = models.TextField()
    image = models.ImageField(upload_to='testimonials/', null=True, blank=True)

    def __str__(self):
        return self.name

class ContactMessage(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='messages_received')
    sender_name = models.CharField(max_length=100)
    sender_email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.sender_name}"

    def __str__(self):
        return f"Message from {self.sender_name}"


