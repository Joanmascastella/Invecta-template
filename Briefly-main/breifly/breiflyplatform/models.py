from django.db import models
from django.utils.timezone import now

# Supabase Users Table Model
class User(models.Model):
    id = models.UUIDField(primary_key=True)  # Supabase's user ID
    email = models.EmailField(unique=True)

    class Meta:
        db_table = '"auth"."users"'
        managed = False  # Prevent Django from managing this table


# Roles Model
class Role(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=50, unique=True)

    class Meta:
        db_table = 'roles'
        managed = False


# User Roles Model
class UserRole(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, db_column='user_id', related_name='user_roles'
    )
    role = models.ForeignKey(
        Role, on_delete=models.CASCADE, db_column='role_id', related_name='user_roles'
    )
    assigned_at = models.DateTimeField(default=now)

    class Meta:
        db_table = 'user_roles'
        managed = False

