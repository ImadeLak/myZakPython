# Generated by Django 2.1 on 2018-08-11 15:42

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import jsonfield.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('api', '0005_situation'),
    ]

    operations = [
        migrations.CreateModel(
            name='Historique',
            fields=[
                ('id_historique', models.AutoField(primary_key=True, serialize=False)),
                ('historique_espece', jsonfield.fields.JSONField()),
                ('historique_immo', jsonfield.fields.JSONField()),
                ('historique_banque', jsonfield.fields.JSONField()),
                ('utilisateur', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
