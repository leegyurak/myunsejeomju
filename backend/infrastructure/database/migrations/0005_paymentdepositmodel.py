# Generated manually for PaymentDepositModel

from django.db import migrations, models
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('database', '0004_ordermodel_pre_order_amount'),
    ]

    operations = [
        migrations.CreateModel(
            name='PaymentDepositModel',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, verbose_name='입금 ID')),
                ('transaction_name', models.CharField(max_length=100, verbose_name='입금자 이름')),
                ('bank_account_number', models.CharField(max_length=50, verbose_name='계좌번호')),
                ('amount', models.PositiveIntegerField(verbose_name='입금 금액')),
                ('bank_code', models.CharField(max_length=10, verbose_name='은행 코드')),
                ('bank_account_id', models.CharField(max_length=255, verbose_name='은행 계좌 ID')),
                ('transaction_date', models.DateTimeField(verbose_name='거래 일시')),
                ('processing_date', models.DateTimeField(verbose_name='처리 일시')),
                ('balance', models.PositiveIntegerField(verbose_name='거래 후 잔액')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='생성일시')),
            ],
            options={
                'verbose_name': '입금 내역',
                'verbose_name_plural': '입금 내역들',
                'db_table': 'payment_deposits',
                'ordering': ['-transaction_date'],
            },
        ),
    ]