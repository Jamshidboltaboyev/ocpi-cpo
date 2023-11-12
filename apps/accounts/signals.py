from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import User, UserGift
from django.utils import timezone


@receiver(pre_save, sender=User)
def check_balance_change(sender, instance, **kwargs):
    if instance.pk:
        old_balance = User.objects.get(pk=instance.pk).balance
        if instance.balance < old_balance:
            active_user_gifts = UserGift.objects.filter(user=instance, status=UserGift.GiftStatus.ACTIVE,
                                                        expired_date__gte=timezone.now().date())
            for user_gift in active_user_gifts:
                user_gift.status = UserGift.GiftStatus.USED
                user_gift.save()
