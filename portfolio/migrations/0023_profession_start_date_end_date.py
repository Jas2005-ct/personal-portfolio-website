from django.db import migrations, models


def convert_years_to_dates(apps, schema_editor):
    Profession = apps.get_model('portfolio', 'Profession')
    for prof in Profession.objects.all():
        prof.start_date = f"{prof.start_year}-01-01"
        if prof.end_year:
            prof.end_date = f"{prof.end_year}-12-31"
        else:
            prof.end_date = None
        prof.save(update_fields=['start_date', 'end_date'])


class Migration(migrations.Migration):

    dependencies = [
        ('portfolio', '0022_delete_client'),
    ]

    operations = [
        migrations.AddField(
            model_name='profession',
            name='start_date',
            field=models.DateField(default='2025-01-01'),
        ),
        migrations.AddField(
            model_name='profession',
            name='end_date',
            field=models.DateField(blank=True, null=True),
        ),
        migrations.RunPython(convert_years_to_dates, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='profession',
            name='start_year',
        ),
        migrations.RemoveField(
            model_name='profession',
            name='end_year',
        ),
    ]
