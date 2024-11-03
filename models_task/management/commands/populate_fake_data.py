from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from faker import Faker
from datetime import timedelta
import random
import string
from models_task.models import Profile, Project, Task, Document, Comment  

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate database with sample data using Faker'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, default=10, help='Number of users to create')
        parser.add_argument('--projects', type=int, default=5, help='Number of projects to create')
        parser.add_argument('--tasks', type=int, default=20, help='Number of tasks to create')
        parser.add_argument('--documents', type=int, default=15, help='Number of documents to create')
        parser.add_argument('--comments', type=int, default=30, help='Number of comments to create')

    def generate_unique_username(self, fake):
        while True:
            # Generate a base username
            username = fake.user_name()
            
            # Add random suffix if needed
            suffix = ''.join(random.choices(string.digits, k=4))
            username = f"{username}{suffix}"
            
            # Check if username exists
            if not User.objects.filter(username=username).exists():
                return username

    def handle(self, *args, **kwargs):
        fake = Faker()
        
        # Get the counts from arguments
        num_users = kwargs['users']
        num_projects = kwargs['projects']
        num_tasks = kwargs['tasks']
        num_documents = kwargs['documents']
        num_comments = kwargs['comments']

        self.stdout.write('Creating users and profiles...')
        users = []
        for i in range(num_users):
            try:
                username = self.generate_unique_username(fake)
                user = User.objects.create_user(
                    username=username,
                    email=f"{username}@example.com",  # Ensure unique email
                    password='password123',
                    first_name=fake.first_name(),
                    last_name=fake.last_name()
                )
                users.append(user)

                # Create corresponding profile
                Profile.objects.create(
                    user=user,
                    role=random.choice([choice[0] for choice in Profile.ROLE_CHOICES]),
                    contact_number=f'+{fake.msisdn()[1:]}'
                )
                
                if (i + 1) % 50 == 0:  # Progress update every 50 users
                    self.stdout.write(f'Created {i + 1} users...')
                    
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error creating user: {str(e)}'))
                continue

        # Skip creating other records if no users were created
        if not users:
            self.stdout.write(self.style.ERROR('No users were created.'))
            return

        self.stdout.write('Creating projects...')
        projects = []
        for i in range(num_projects):
            try:
                start_date = fake.date_between(start_date='-1y', end_date='today')
                end_date = fake.date_between(start_date=start_date, end_date=start_date + timedelta(days=180))
                
                project = Project.objects.create(
                    title=f"{fake.catch_phrase()} {i+1}",  # Add number to ensure unique titles
                    description=fake.text(max_nb_chars=200),
                    start_date=start_date,
                    end_date=end_date
                )
                # Add random team members
                team_members = random.sample(users, random.randint(2, min(5, len(users))))
                project.team_members.set(team_members)
                projects.append(project)
                
                if (i + 1) % 50 == 0:  # Progress update every 50 projects
                    self.stdout.write(f'Created {i + 1} projects...')
                    
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error creating project: {str(e)}'))
                continue

        # Skip creating tasks and documents if no projects were created
        if not projects:
            self.stdout.write(self.style.ERROR('No projects were created. Aborting...'))
            return

        self.stdout.write('Creating tasks...')
        tasks = []
        for i in range(num_tasks):
            try:
                project = random.choice(projects)
                possible_assignees = list(project.team_members.all())
                
                task = Task.objects.create(
                    title=f"{fake.sentence(nb_words=6)} {i+1}",  # Add number to ensure unique titles
                    description=fake.text(max_nb_chars=200),
                    status=random.choice([choice[0] for choice in Task.STATUS_CHOICES]),
                    project=project,
                    assignee=random.choice(possible_assignees) if possible_assignees else None
                )
                tasks.append(task)
                
                if (i + 1) % 50 == 0:  # Progress update every 50 tasks
                    self.stdout.write(f'Created {i + 1} tasks...')
                    
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error creating task: {str(e)}'))
                continue

        self.stdout.write('Creating documents...')
        for i in range(num_documents):
            try:
                Document.objects.create(
                    name=f"{fake.file_name()} {i+1}",  # Add number to ensure unique names
                    description=fake.text(max_nb_chars=100),
                    file='dummy_file.pdf',
                    version=f'{random.randint(1, 5)}.{random.randint(0, 9)}',
                    project=random.choice(projects)
                )
                
                if (i + 1) % 50 == 0:  # Progress update every 50 documents
                    self.stdout.write(f'Created {i + 1} documents...')
                    
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error creating document: {str(e)}'))
                continue

        self.stdout.write('Creating comments...')
        for i in range(num_comments):
            try:
                # Randomly choose between commenting on a task or project
                if random.choice([True, False]) and tasks:
                    target_task = random.choice(tasks)
                    target_project = None
                else:
                    target_task = None
                    target_project = random.choice(projects)

                Comment.objects.create(
                    text=fake.paragraph(),
                    author=random.choice(users),
                    task=target_task,
                    project=target_project
                )
                
                if (i + 1) % 50 == 0:  # Progress update every 50 comments
                    self.stdout.write(f'Created {i + 1} comments...')
                    
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'Error creating comment: {str(e)}'))
                continue

        self.stdout.write(self.style.SUCCESS('Successfully populated the database with sample data!'))