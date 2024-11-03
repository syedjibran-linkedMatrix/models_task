from django.db import models

from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator

User = get_user_model()


class Profile(models.Model):
    ROLE_CHOICES = [
        ("manager", "Project Manager"),
        ("qa", "Quality Assurance"),
        ("developer", "Developer"),
        ("designer", "Designer"),
        ("product_owner", "Product Owner"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    profile_picture = models.ImageField(
        upload_to="profile_pics/", null=True, blank=True
    )
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default="developer")
    contact_number = models.CharField(
        max_length=25,
        validators=[
            RegexValidator(
                regex=r"^\+?1?\d{9,15}$",
                message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed.",
            )
        ],
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


class Project(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    team_members = models.ManyToManyField(User, related_name="projects", blank=True)

    def __str__(self):
        return self.title


class Task(models.Model):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("review", "In Review"),
        ("working", "In Progress"),
        ("awaiting_release", "Awaiting Release"),
        ("waiting_qa", "Waiting for QA"),
        ("completed", "Completed"),
        ("closed", "Closed"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="tasks")
    assignee = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_tasks",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} - {self.get_status_display()}"


class Document(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    file = models.FileField(upload_to="project_documents/")
    version = models.CharField(max_length=50)
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="documents"
    )
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} (v{self.version})"


class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    task = models.ForeignKey(
        Task, on_delete=models.CASCADE, related_name="comments", null=True, blank=True
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name="comments",
        null=True,
        blank=True,
    )

    def __str__(self):
        return f"Comment by {self.author.username} on {self.created_at}"

    class Meta:
        ordering = ["-created_at"]
