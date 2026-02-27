"""
Initial migration for tracker app - Project, Contributor, Issue, Comment models.
"""

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Project',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('type', models.CharField(choices=[('back-end', 'Back-end'), ('front-end', 'Front-end'), ('iOS', 'iOS'), ('Android', 'Android')], max_length=20)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('updated_time', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='authored_projects', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Project',
                'verbose_name_plural': 'Projects',
                'ordering': ['-created_time'],
            },
        ),
        migrations.CreateModel(
            name='Issue',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField()),
                ('priority', models.CharField(choices=[('LOW', 'Low'), ('MEDIUM', 'Medium'), ('HIGH', 'High')], default='MEDIUM', max_length=10)),
                ('tag', models.CharField(choices=[('BUG', 'Bug'), ('FEATURE', 'Feature'), ('TASK', 'Task')], default='TASK', max_length=20)),
                ('status', models.CharField(choices=[('To Do', 'To Do'), ('In Progress', 'In Progress'), ('Finished', 'Finished')], default='To Do', max_length=20)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('updated_time', models.DateTimeField(auto_now=True)),
                ('assignee', models.ForeignKey(blank=True, help_text='Must be a contributor of the project', null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_issues', to=settings.AUTH_USER_MODEL)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_issues', to=settings.AUTH_USER_MODEL)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='issues', to='tracker.project')),
            ],
            options={
                'verbose_name': 'Issue',
                'verbose_name_plural': 'Issues',
                'ordering': ['-created_time'],
            },
        ),
        migrations.CreateModel(
            name='Comment',
            fields=[
                ('uuid', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('description', models.TextField()),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('updated_time', models.DateTimeField(auto_now=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_comments', to=settings.AUTH_USER_MODEL)),
                ('issue', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='comments', to='tracker.issue')),
            ],
            options={
                'verbose_name': 'Comment',
                'verbose_name_plural': 'Comments',
                'ordering': ['-created_time'],
            },
        ),
        migrations.CreateModel(
            name='Contributor',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('role', models.CharField(choices=[('author', 'Author'), ('contributor', 'Contributor')], default='contributor', max_length=20)),
                ('created_time', models.DateTimeField(auto_now_add=True)),
                ('project', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contributors', to='tracker.project')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='contributor_projects', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Contributor',
                'verbose_name_plural': 'Contributors',
                'ordering': ['-created_time'],
                'unique_together': {('user', 'project')},
            },
        ),
    ]
