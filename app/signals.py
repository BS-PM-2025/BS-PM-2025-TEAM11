from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Student, Secretary, AcademicStaff

@receiver(post_save, sender=User)
def create_profile_for_user(sender, instance, created, **kwargs):
    if created:
        if instance.role == 'secretary':
            Secretary.objects.get_or_create(user=instance)
        elif instance.role == 'academic':
            AcademicStaff.objects.get_or_create(user=instance)
        # 🧑‍🎓 הסרנו יצירת Student – כי הוא נוצר ידנית ב־View
