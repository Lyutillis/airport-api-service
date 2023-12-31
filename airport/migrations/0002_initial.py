# Generated by Django 4.1 on 2023-12-11 12:58

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('airport', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='order',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='orders', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='flight',
            name='airplane',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='flights', to='airport.airplane'),
        ),
        migrations.AddField(
            model_name='flight',
            name='route',
            field=models.ForeignKey(on_delete=django.db.models.deletion.DO_NOTHING, related_name='flights', to='airport.route'),
        ),
        migrations.AddField(
            model_name='crewflight',
            name='crew',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='crew_flights', to='airport.crew'),
        ),
        migrations.AddField(
            model_name='crewflight',
            name='flight',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='flight_crews', to='airport.flight'),
        ),
        migrations.AddField(
            model_name='airplane',
            name='airplane_type',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='airplanes', to='airport.airplanetype'),
        ),
    ]
