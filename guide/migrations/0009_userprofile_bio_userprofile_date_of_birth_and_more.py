# Generated by Django 5.1 on 2024-09-25 06:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('guide', '0008_userprofile_delete_profile'),
    ]

    operations = [
       
        migrations.AddField(
            model_name='userprofile',
            name='date_of_birth',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='userprofile',
            name='gender',
            field=models.CharField(blank=True, choices=[('M', 'Male'), ('F', 'Female'), ('O', 'Other')], max_length=1, null=True),
        ),
      
        migrations.AddField(
            model_name='userprofile',
            name='phone_number',
            field=models.CharField(blank=True, max_length=15, null=True),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='profile_picture',
            field=models.ImageField(blank=True, upload_to='profile_pics'),
        ),
       
    ]
