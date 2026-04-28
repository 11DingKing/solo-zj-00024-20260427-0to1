from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Album',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('cover_image', models.ImageField(blank=True, null=True, upload_to='album_covers/')),
                ('is_public', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='albums', to='accounts.customuser')),
            ],
            options={
                'db_table': 'albums',
                'ordering': ['-created_at'],
            },
        ),
        migrations.AddIndex(
            model_name='album',
            index=models.Index(fields=['owner', '-created_at'], name='albums_owner_id_437445_idx'),
        ),
        migrations.AddIndex(
            model_name='album',
            index=models.Index(fields=['is_public', '-created_at'], name='albums_is_publi_494158_idx'),
        ),
    ]
