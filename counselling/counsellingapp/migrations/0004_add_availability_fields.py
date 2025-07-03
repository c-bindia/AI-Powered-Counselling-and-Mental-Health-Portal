from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('counsellingapp', '0003_alter_counselor_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='counselor',
            name='availability_start',
            field=models.TimeField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='counselor',
            name='availability_end',
            field=models.TimeField(null=True, blank=True),
        ),
    ]
