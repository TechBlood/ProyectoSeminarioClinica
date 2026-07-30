from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('auth', '0012_alter_user_first_name_max_length'),
        ('admin', '0003_logentry_add_action_flag_choices'),
        ('contenttypes', '0002_remove_content_type_name'),
        ('sessions', '0001_initial'),
    ]

    operations = [
        # Use ALTER TABLE ... RENAME TO for SQLite compatibility (MySQL uses 'RENAME TABLE')
        migrations.RunSQL(
            sql='ALTER TABLE auth_group RENAME TO grupos;',
            reverse_sql='ALTER TABLE grupos RENAME TO auth_group;',
        ),
        migrations.RunSQL(
            sql='ALTER TABLE auth_permission RENAME TO permisos;',
            reverse_sql='ALTER TABLE permisos RENAME TO auth_permission;',
        ),
        migrations.RunSQL(
            sql='ALTER TABLE auth_group_permissions RENAME TO grupos_permisos;',
            reverse_sql='ALTER TABLE grupos_permisos RENAME TO auth_group_permissions;',
        ),
        migrations.RunSQL(
            sql='ALTER TABLE django_content_type RENAME TO tipos_contenido;',
            reverse_sql='ALTER TABLE tipos_contenido RENAME TO django_content_type;',
        ),
        migrations.RunSQL(
            sql='ALTER TABLE django_session RENAME TO sesiones;',
            reverse_sql='ALTER TABLE sesiones RENAME TO django_session;',
        ),
        migrations.RunSQL(
            sql='ALTER TABLE django_admin_log RENAME TO registros_admin;',
            reverse_sql='ALTER TABLE registros_admin RENAME TO django_admin_log;',
        ),
    ]
