# Generated by Django 3.1.1 on 2021-02-14 02:39

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('doctors', '0003_doctorprofile_proof'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='PatientProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date_of_birth', models.DateField()),
                ('profilePicture', models.ImageField(upload_to='profilePics')),
                ('addressline1', models.CharField(default=' ', max_length=200)),
                ('addressline2', models.CharField(default=' ', max_length=200)),
                ('country', models.CharField(max_length=200)),
                ('city', models.CharField(max_length=200)),
                ('zipcode', models.CharField(max_length=12)),
                ('sex', models.CharField(max_length=20)),
                ('pronouns', models.CharField(max_length=100)),
                ('race', models.CharField(max_length=200)),
                ('number', models.CharField(max_length=20)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='TreatmentsandMedicines',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('medicine', models.CharField(max_length=200)),
                ('decription', models.CharField(max_length=200)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patients.patientprofile')),
            ],
        ),
        migrations.CreateModel(
            name='Lifestyle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('activity', models.CharField(max_length=200)),
                ('amount', models.CharField(max_length=200)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patients.patientprofile')),
            ],
        ),
        migrations.CreateModel(
            name='HealthConditions',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patients.patientprofile')),
            ],
        ),
        migrations.CreateModel(
            name='Document',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('pdf', models.FileField(upload_to='prescription_pdfs')),
                ('issued_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='doctors.doctorprofile')),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patients.patientprofile')),
            ],
        ),
        migrations.CreateModel(
            name='Allergies',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=200)),
                ('patient', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='patients.patientprofile')),
            ],
        ),
    ]