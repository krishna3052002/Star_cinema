# Generated by Django 4.1 on 2025-06-25 08:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('star_cinema_app', '0006_booking_seattype_seat_bookingseat'),
    ]

    operations = [
        migrations.RenameField(
            model_name='theater',
            old_name='seat_capacity',
            new_name='columns',
        ),
        migrations.AddField(
            model_name='theater',
            name='rows',
            field=models.IntegerField(default=60),
            preserve_default=False,
        ),
    ]
