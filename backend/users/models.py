from datetime import timedelta

from django.conf import settings
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.contrib.contenttypes.fields import GenericRelation
from django.core.mail import send_mail
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from backend.notifications.models import Notification
from backend.users.managers import CustomUserManager


def current_date():
    return timezone.now().date()


def current_time():
    return timezone.now().time()


def get_user_trial_period():
    return timezone.now() + timedelta(days=settings.USER_TRIAL_PERIOD)


class User(AbstractBaseUser, PermissionsMixin):
    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    class Gender(models.TextChoices):
        MALE = 'M', _('Male')
        FEMALE = 'F', _('Female')
        UNKNOWN = 'U', _('Unknown')

    class MaritalStatus(models.TextChoices):
        SINGLE = 'S', _('Single')
        MARRIED = 'M', _('Married')
        DIVORCED = 'D', _('Divorced')
        OTHER = 'O', _('Other')

    class LookingForStatus(models.TextChoices):
        SINGLE = 'S', _('Single')
        MARRIED = 'M', _('Married')
        DIVORCED = 'D', _('Divorced')
        NO_PREFERENCE = 'N', _('No Preference')

    class BloodGroup(models.TextChoices):
        AB_NEGATIVE = 'AB-', _('AB-')
        AB_POSITIVE = 'AB+', _('AB+')
        A_NEGATIVE = 'A-', _('A-')
        A_POSITIVE = 'A+', _('A+')
        B_NEGATIVE = 'B-', _('B-')
        B_POSITIVE = 'B+', _('B+')
        O_NEGATIVE = 'O-', _('O-')
        O_POSITIVE = 'O+', _('O+')
        UNKNOWN = 'U', _('Unknown')

    class CreatedBy(models.TextChoices):
        SELF = 'SELF', _('Self')
        PARENT = 'PARENT', _('Parent')
        GUARDIAN = 'GUARDIAN', _('Guardian')
        SIBLING = 'SIBLING', _('Sibling')
        FRIEND = 'FRIEND', _('Friend')
        OTHER = 'OTHER', _('Other')

    class Religion(models.TextChoices):
        CHRISTIANITY = 'CHRISTIANITY', _('Christianity')
        ISLAM = 'ISLAM', _('Islam')
        ATHEIST = 'ATHEIST', _('Atheist')
        HINDUISM = 'HINDUISM', _('Hinduism')
        BUDDHISM = 'BUDDHISM', _('Buddhism')
        SIKHISM = 'SIKHISM', _('Sikhism')
        SPIRITISM = 'SPIRITISM', _('Spiritism')
        JUDAISM = 'JUDAISM', _('Judaism')
        OTHER = 'OTHER', _('Other')

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    objects = CustomUserManager()
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_('Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    first_name = models.CharField(_('first name'), max_length=150, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    email = models.EmailField(_('email address'), unique=True)
    contact_number = models.CharField(_('contact number'), max_length=16, blank=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_('Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(
        _('date joined'),
        default=timezone.now
    )

    date_of_birth = models.DateField(
        _('date of birth'),
        default=current_date
    )
    time_of_birth = models.TimeField(
        _('time of birth'),
        default=current_time
    )
    city_of_birth = models.CharField(
        _('city of birth'),
        max_length=64,
        null=True,
        blank=True
    )
    country = models.CharField(
        _('country'),
        max_length=64,
        null=True,
        blank=True
    )
    city = models.CharField(
        _('city'),
        max_length=64,
        null=True,
        blank=True
    )
    zip_code = models.CharField(
        _('zip code'),
        max_length=32,
        null=True,
        blank=True
    )
    residency_status = models.CharField(
        _('residency status'),
        max_length=64,
        null=True,
        blank=True
    )
    highest_qualification = models.CharField(
        _('highest qualification'),
        max_length=128,
        null=True,
        blank=True
    )
    employer = models.CharField(
        _('employer'),
        max_length=128,
        null=True,
        blank=True
    )
    designation = models.CharField(
        _('employer'),
        max_length=128,
        null=True,
        blank=True
    )
    annual_income = models.IntegerField(
        _('annual income'),
        default=0
    )
    religion = models.CharField(
        _('religion'),
        max_length=32,
        choices=Religion.choices,
        default=Religion.OTHER,
    )
    mother_tongue = models.CharField(
        _('mother tongue'),
        max_length=64,
        null=True,
        blank=True
    )
    community = models.CharField(
        _('community'),
        max_length=64,
        null=True,
        blank=True
    )
    sub_community = models.CharField(
        _('sub-community'),
        max_length=64,
        null=True,
        blank=True
    )
    gender = models.CharField(
        _('gender'),
        max_length=1,
        choices=Gender.choices,
        default=Gender.UNKNOWN,
    )
    marital_status = models.CharField(
        _('marital status'),
        max_length=1,
        choices=MaritalStatus.choices,
        default=MaritalStatus.SINGLE,
    )
    looking_for = models.CharField(
        _('looking for'),
        max_length=1,
        choices=LookingForStatus.choices,
        default=LookingForStatus.NO_PREFERENCE,
    )
    blood_group = models.CharField(
        _('blood group'),
        max_length=3,
        choices=BloodGroup.choices,
        default=BloodGroup.UNKNOWN,
    )
    created_by = models.CharField(
        _('created by'),
        max_length=8,
        choices=CreatedBy.choices,
        default=CreatedBy.SELF,
    )
    height = models.PositiveSmallIntegerField(
        _('height'),
        default=0,
        help_text='height in centimeters'
    )
    has_disability = models.BooleanField(
        _('has disability'),
        default=False
    )
    is_father_alive = models.BooleanField(
        _('is father alive'),
        default=True
    )
    is_mother_alive = models.BooleanField(
        _('is mother alive'),
        default=True
    )
    children_count = models.PositiveSmallIntegerField(
        _('children count'),
        default=0
    )
    brothers_count = models.PositiveSmallIntegerField(
        _('brothers count'),
        default=0
    )
    sisters_count = models.PositiveSmallIntegerField(
        _('sisters count'),
        default=0
    )
    avatar = models.ImageField(upload_to='avatar', null=True, blank=True)

    about_self = models.CharField(_('about self'), max_length=2048, null=True, blank=True)
    about_family = models.CharField(_('about family'), max_length=2048, null=True, blank=True)
    about_partner = models.CharField(_('about partner'), max_length=2048, null=True, blank=True)
    about_likes = models.CharField(_('about likes'), max_length=1024, null=True, blank=True)
    about_dislikes = models.CharField(_('about dislikes'), max_length=1024, null=True, blank=True)
    about_lifestyle = models.CharField(_('about lifestyle'), max_length=1024, null=True, blank=True)

    payment_plan = models.ForeignKey(
        'payments.PaymentPlan',
        on_delete=models.PROTECT,
        related_name='subscribers',
        null=True, blank=True
    )
    payment_plan_subscribed_at = models.DateTimeField(_('payment plan subscribed at'), default=timezone.now)
    payment_plan_expires_at = models.DateTimeField(_('payment plan expires at'), default=get_user_trial_period)

    created_at = models.DateTimeField(_('created at'), default=timezone.now)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """
        Return the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Send an email to this user."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    @property
    def is_payment_plan_expired(self):
        return self.payment_plan_expires_at <= timezone.now()

    @property
    def payment_plan_title(self):
        return self.payment_plan.title if self.payment_plan else None


class Sentiment(models.Model):
    class Meta:
        unique_together = ['sentiment_to', 'sentiment_from']

    class SentimentStatus(models.TextChoices):
        LIKE = 'L', _('LIKE')
        DISLIKE = 'D', _('DISLIKE')
        NEUTRAL = 'N', _('NEUTRAL')

    sentiment_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sentiments_to')
    sentiment_from = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sentiments_from')
    sentiment = models.CharField(
        _('sentiment'),
        max_length=1,
        choices=SentimentStatus.choices,
        default=SentimentStatus.NEUTRAL,
    )

    notifications = GenericRelation(Notification, related_query_name='sentiments')

    created_at = models.DateTimeField(_('created at'), default=timezone.now)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)


class ProfileView(models.Model):
    viewer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='viewer')
    viewee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='viewee')

    notifications = GenericRelation(Notification, related_query_name='profile_views')

    created_at = models.DateTimeField(_('created at'), default=timezone.now)
