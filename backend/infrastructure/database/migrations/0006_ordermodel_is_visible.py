# Generated manually for is_visible field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0005_paymentdepositmodel'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordermodel',
            name='is_visible',
            field=models.BooleanField(default=True, verbose_name='표시 여부'),
        ),
    ]