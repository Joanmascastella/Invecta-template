from django.db import models
from django.utils.timezone import now

# Supabase Users Table Model
class User(models.Model):
    id = models.UUIDField(primary_key=True)  
    email = models.EmailField(unique=True)

    class Meta:
        db_table = '"auth"."users"'
        managed = False  

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

# Item Model
class Item(models.Model):
    id = models.UUIDField(primary_key=True)  
    serial_number = models.TextField()
    provider = models.TextField(blank=True, null=True)
    name = models.TextField()
    category = models.TextField(blank=True, null=True)

    class Meta:
        db_table = 'items'
        managed = False  

# Previous Offer Model
class PreviousOffer(models.Model):
    id = models.UUIDField(primary_key=True)  
    items = models.JSONField()
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, db_column='user_id', related_name='previous_offers'
    )

    class Meta:
        db_table = 'previous_offers'
        managed = False  
