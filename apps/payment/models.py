from django.db import models
from django.utils.translation import gettext as _
from apps.accounts.models import User

from django.db import models
from django.utils.translation import gettext_lazy as _
from payments.models import BasePayment

from apps.accounts.models import User


class Transaction(BasePayment):
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name="transactions")
    paid_at = models.DateTimeField(verbose_name=_("Paid At"), null=True, blank=True)
    cancel_time = models.DateTimeField(verbose_name=_("Cancel Time"), null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta(BasePayment.Meta):
        unique_together = ("variant", "transaction_id")

    def save(self, *args, **kwargs):
        # If transaction_id is not provided, set it to the id field"
        if not self.transaction_id or self.transaction_id == "" or self.transaction_id == "None":
            self.transaction_id = str(self.id)
        super().save(*args, **kwargs)


class Provider(models.TextChoices):
    PAYME = "payme", _("Payme")
    CLICK = "click", _("Click")
    PAYLOV = "paylov", _("Paylov")
    UZUM_BANK = "uzum_bank", _("Uzum Bank")
    CARD = "card", _("Card")


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("Created at"))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_("Updated at"))

    class Meta:
        abstract = True


class PaymentMerchantRequestLog(TimeStampedModel):
    provider = models.CharField(max_length=63, verbose_name=_("Provider"), choices=Provider.choices)
    header = models.TextField(verbose_name=_("Header"))
    body = models.TextField(verbose_name=_("Body"))
    method = models.CharField(verbose_name=_("Method"), max_length=32)
    response = models.TextField(null=True, blank=True)
    response_status_code = models.IntegerField(null=True, blank=True)
    type = models.CharField(max_length=32)

    class Meta:
        verbose_name = _("Payment Merchant Request Log")
        verbose_name_plural = _("Payment Merchant Request Logs")


class DiscountUser(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="discount_user")
    discount = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    end_date = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Discount User")
        verbose_name_plural = _("Discount Users")

    def __str__(self):
        return f"{self.user}"


class MinBalance(models.Model):
    amount = models.IntegerField(default=0, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _("Min Balance")
        verbose_name_plural = _("Min Balances")


class UserCard(TimeStampedModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name=_("User"))
    card_number = models.CharField(max_length=255, verbose_name=_("Card Number"))
    expire_date = models.CharField(max_length=255, verbose_name=_("Expire Date"))
    card_id = models.CharField(max_length=255, verbose_name=_("Card ID"))
    token = models.CharField(max_length=255, verbose_name=_("Token"), null=True)
    confirmed = models.BooleanField(default=False, verbose_name=_("Confirmed"))

    class Meta:
        verbose_name = _("User Card")
        verbose_name_plural = _("User Cards")
        unique_together = ("user", "card_number")


class UserPaymentStatus(models.Model):
    title = models.CharField(_("Заголовок"), max_length=256)
    status = models.BooleanField(_("Статус"), default=True)
    created_at = models.DateTimeField(_("Vaqt"), auto_now_add=True)
    updated_at = models.DateTimeField(_("Vaqt"), auto_now=True)

    class Meta:
        verbose_name = _("Статус платежа")
        verbose_name_plural = _("Статусы платежа")

    def __str__(self):
        return self.title


class UserBalanceHistory(models.Model):
    OPERATION = (
        (1, _("Hisob to'ldirildi")),
        (2, _("Hisob raqamidan pul yechib olindi")),
    )

    user = models.ForeignKey(User, verbose_name=_("Foydalanuvchi"), on_delete=models.PROTECT)
    amount = models.FloatField(_("Summa"))
    operation = models.IntegerField(_("Bajarilgan amal"), choices=OPERATION)
    prev_balance = models.FloatField(_("O'zgarishdan oldingi balans"))
    new_balance = models.FloatField(_("O'zgarishdan keyingi balans"))
    comment = models.TextField(_("Qo'shimcha ma'lumot"), null=True, blank=True)
    created_at = models.DateTimeField(_("Vaqt"), auto_now_add=True)
    title = models.CharField(_("Title"), max_length=256)
    connector_id = models.IntegerField(_("Connector id"), null=True, blank=True)
    charge_transaction_id = models.IntegerField(_("Charge transaction id"), null=True, blank=True)
    transaction = models.ForeignKey(Transaction, on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        verbose_name = _("Foydalanuvchi hisobi tarixi")
        verbose_name_plural = _("Foydalanuvchi hisobi tarixlari")

    def __str__(self):
        return "{0} - {1} - {2}".format(
            self.user.get_full_name, str(self.amount), self.created_at.strftime("%d.%m.%Y %H:%M")
        )
