from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('albums', '0001_initial'),
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
                'db_table': 'tags',
                'ordering': ['name'],
            },
        ),
        migrations.CreateModel(
            name='Photo',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=255, null=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('original_image', models.ImageField(upload_to='photos/original/')),
                ('thumbnail_small', models.ImageField(blank=True, null=True, upload_to='photos/thumbs/small/')),
                ('thumbnail_medium', models.ImageField(blank=True, null=True, upload_to='photos/thumbs/medium/')),
                ('thumbnail_large', models.ImageField(blank=True, null=True, upload_to='photos/thumbs/large/')),
                ('exif_camera_make', models.CharField(blank=True, max_length=100, null=True)),
                ('exif_camera_model', models.CharField(blank=True, max_length=100, null=True)),
                ('exif_lens_model', models.CharField(blank=True, max_length=100, null=True)),
                ('exif_focal_length', models.CharField(blank=True, max_length=50, null=True)),
                ('exif_aperture', models.CharField(blank=True, max_length=50, null=True)),
                ('exif_shutter_speed', models.CharField(blank=True, max_length=50, null=True)),
                ('exif_iso', models.IntegerField(blank=True, null=True)),
                ('exif_flash', models.BooleanField(blank=True, null=True)),
                ('exif_white_balance', models.CharField(blank=True, max_length=50, null=True)),
                ('exif_datetime_original', models.DateTimeField(blank=True, null=True)),
                ('exif_gps_latitude', models.FloatField(blank=True, null=True)),
                ('exif_gps_longitude', models.FloatField(blank=True, null=True)),
                ('exif_gps_altitude', models.FloatField(blank=True, null=True)),
                ('file_size', models.IntegerField(default=0)),
                ('image_width', models.IntegerField(blank=True, null=True)),
                ('image_height', models.IntegerField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('album', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='albums.album')),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='photos', to='accounts.customuser')),
                ('tags', models.ManyToManyField(blank=True, related_name='photos', to='photos.tag')),
            ],
            options={
                'db_table': 'photos',
                'ordering': ['-exif_datetime_original', '-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='photo',
            index=models.Index(fields=['album', '-exif_datetime_original'], name='photos_album_id_752485_idx'),
        ),
        migrations.AddIndex(
            model_name='photo',
            index=models.Index(fields=['owner', '-exif_datetime_original'], name='photos_owner_id_2e2d0e_idx'),
        ),
        migrations.AddIndex(
            model_name='photo',
            index=models.Index(fields=['-exif_datetime_original'], name='photos_exif_da_4c05c2_idx'),
        ),
    ]
