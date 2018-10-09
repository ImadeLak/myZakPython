# Generated by Django 2.0.6 on 2018-06-24 17:01

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0003_departement_mon_utilisateur'),
    ]

    operations = [
        migrations.CreateModel(
            name='Banque',
            fields=[
                ('id_banque', models.AutoField(primary_key=True, serialize=False)),
                ('nom_banque', models.CharField(max_length=50)),
                ('urlLogin_banque', models.CharField(max_length=500)),
                ('urlHome_banque', models.CharField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='CompteBancaire',
            fields=[
                ('id_compteBancaire', models.AutoField(primary_key=True, serialize=False)),
                ('login_compteBancaire', models.CharField(max_length=50)),
                ('password_compteBancaire', models.CharField(max_length=50)),
                ('banque', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.Banque')),
                ('utilisateur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]