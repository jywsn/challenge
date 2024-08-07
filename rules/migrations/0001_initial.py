# Generated by Django 4.2.14 on 2024-07-18 08:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('users', '0002_school_user_school'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ApplicationRule',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
        ),
        migrations.CreateModel(
            name='Condition',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('label', models.CharField(max_length=256)),
                ('application_field_name', models.CharField(max_length=256)),
                ('application_field_value', models.CharField(max_length=256)),
            ],
        ),
        migrations.CreateModel(
            name='RuleAction',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action_type', models.CharField(choices=[('DRQ', 'Document Request')], max_length=3)),
                ('application_rule', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rules.applicationrule')),
            ],
        ),
        migrations.CreateModel(
            name='RuleDocument',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('document_type', models.CharField(choices=[('BTD', 'Business Tax Documents'), ('W2A', 'W2 - Parent A (Previous Year)')], max_length=3)),
                ('description', models.CharField(blank=True, max_length=256)),
                ('rule_action', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='rules.ruleaction')),
            ],
        ),
        migrations.AddField(
            model_name='applicationrule',
            name='conditions',
            field=models.ManyToManyField(to='rules.condition'),
        ),
        migrations.AddField(
            model_name='applicationrule',
            name='school',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.school'),
        ),
        migrations.CreateModel(
            name='Application',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_returning', models.BooleanField(blank=True, default=False)),
                ('is_business_owner', models.BooleanField(blank=True, default=False)),
                ('did_file_2021_us_taxes', models.BooleanField(blank=True, default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
