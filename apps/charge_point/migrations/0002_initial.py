# Generated by Django 4.2 on 2023-11-11 11:33

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('vehicle', '0001_initial'),
        ('charge_point', '0001_initial'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='chargetransaction',
            name='vehicle',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='transactions', to='vehicle.vehicle'),
        ),
        migrations.AddField(
            model_name='chargepointtask',
            name='connector',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='charge_point.connector'),
        ),
        migrations.AddField(
            model_name='chargepointtask',
            name='transaction',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='task', to='charge_point.inprogresstransaction'),
        ),
        migrations.AddField(
            model_name='chargepointtask',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='tasks', to='accounts.user'),
        ),
        migrations.AddField(
            model_name='chargepointtask',
            name='vehicle',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.PROTECT, related_name='charge_tasks', to='vehicle.vehicle'),
        ),
        migrations.AddField(
            model_name='chargepointerror',
            name='connector_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='errors', to='charge_point.connector', verbose_name='Коннектор'),
        ),
        migrations.AddField(
            model_name='chargepoint',
            name='address',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='charge_point.address', verbose_name='Адрес'),
        ),
        migrations.AddField(
            model_name='authorizationrequest',
            name='charge_point',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='charge_point.chargepoint', verbose_name='Станция'),
        ),
        migrations.AddField(
            model_name='authorizationrequest',
            name='token',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='charge_point.token'),
        ),
        migrations.AddField(
            model_name='address',
            name='region',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='address', to='charge_point.region', verbose_name='Регион'),
        ),
        migrations.AlterUniqueTogether(
            name='favoritechargepoint',
            unique_together={('charger_point', 'user')},
        ),
        migrations.AlterUniqueTogether(
            name='favoriteaddress',
            unique_together={('address', 'user')},
        ),
        migrations.AlterUniqueTogether(
            name='connector',
            unique_together={('charge_point_id', 'connector_id')},
        ),
    ]
