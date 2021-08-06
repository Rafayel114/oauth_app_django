from django.db import models
from django.contrib.auth.models import AbstractUser, User, BaseUserManager
from django.utils import timezone
from accounts.managers import CustomUserManager
from django.utils.translation import ugettext_lazy as _
from phonenumber_field.modelfields import PhoneNumberField
from oauth2_provider.models import AbstractApplication


# to get phone_number as str use CustomUser.phone_number.as_e164
class CustomUser(AbstractUser):
    username = None
    phone_number = PhoneNumberField(null=False, blank=False, unique=True)
    email = models.EmailField(_('email address'), unique=True)
    sms_code = models.IntegerField(blank=True, null=True)
    balance = models.FloatField(default=0.0)
    rating = models.FloatField(default=1.0)


    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []


    def __str__(self):
        return self.email

    def getUserGroup(self):
        user_group = UserGroup.objects.get(user=self)
        group = user_group.group.name
        return group

    @staticmethod
    def setUserGroup(self, group):
        if group == 'Courier':
            app = CustomApplication.objects.get(name='DeliFast')
            group = CustomGroup.objects.get(name='Courier')
            new_group = UserGroup.objects.create(user=self, application=app, group=group)
            new_group.save()
        else:
            deli = CustomApplication.objects.get(name='DeliFast')
            group = CustomGroup.objects.get(name='Client')
            new_deli_user = UserGroup.objects.create(user=self, application=deli, group=group)
            new_deli_user.save()



class CustomApplication(AbstractApplication):
    hidden = models.BooleanField(default=True)
    logo = models.ImageField(upload_to="media/app_logo", blank=True)
    address = models.CharField(blank=True, max_length=200)
    # key = models.CharField(blank=True, max_length=200)

    class Meta:
        verbose_name = "Приложение"
        verbose_name_plural = "Приложения"


class CustomUserFields(models.Model):
    user = models.ForeignKey('CustomUser', blank=False, null=False, on_delete=models.CASCADE)
    application = models.ForeignKey('CustomApplication', blank=False, null=False, on_delete=models.CASCADE)
    name = models.CharField(max_length=200, blank=False, null=False)
    value = models.TextField()


class CustomGroup(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Группа"
        verbose_name_plural = "Группы"


class UserGroup(models.Model):
    user = models.ForeignKey('CustomUser', blank=False, null=False, on_delete=models.CASCADE)
    application = models.ForeignKey('CustomApplication', blank=False, null=False, on_delete=models.CASCADE)
    group = models.ForeignKey('CustomGroup', blank=False, null=False, on_delete=models.CASCADE)

    def __str__(self):
        return f"User: {self.user}, App: {self.application}, Group: {self.group}"

class Transaction(models.Model):

    value = models.FloatField(default=0.0)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_transaction')
    custom_field = models.ForeignKey(CustomUserFields, on_delete=models.DO_NOTHING, blank=True, null=True)
    application = models.ForeignKey(CustomApplication, on_delete=models.DO_NOTHING, blank=True, null=True)
    parentTransaction = models.ForeignKey('self', on_delete=models.DO_NOTHING, blank=True, null=True)
    creationDate = models.DateTimeField(default=timezone.now, editable=False)
    transactionDate = models.DateTimeField(default=timezone.now)
    comment = models.TextField(blank=True, verbose_name='Комментарий')
    archival = models.BooleanField(default=False, verbose_name='Архивная')
    TYPE_CHOICES = (
        (1, 'Неопределён'),
        (2, 'Расчёт'),
        (3, 'Приём средств'),
        (4, 'Оказание услуги'),
        (5, 'Комиссия'),
        (6, 'Скидка'),
        (7, 'Чаевые'),
        (8, 'Выплата ЗП'),
    )
    type = models.IntegerField(
        choices=TYPE_CHOICES,
        default=1,
        verbose_name='Тип транзакции',
    )
    PAYMENTTYPE_CHOICES = (
        (1, 'Нет'),
        (2, 'Наличные'),
        (3, 'Юр.счет'),
        (4, 'Физ.счет'),
    )
    paymentType = models.IntegerField(
        choices=PAYMENTTYPE_CHOICES,
        default=1,
        verbose_name='Способ оплаты',
    )


class UserApp(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    application = models.ForeignKey(CustomApplication, on_delete=models.CASCADE)
