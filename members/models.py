from django.db import models
from django.contrib.auth.models import User

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class Zone(models.Model):
    name = models.CharField(max_length=100, unique=True)
    representative = models.ForeignKey(
    User,
    on_delete=models.SET_NULL,
    null=True,
    blank=True,
    related_name='managed_zones'
    )
    def __str__(self):
        return self.name


class Member(models.Model):
    full_name = models.CharField(max_length=200)
    date_of_birth = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    course = models.CharField(
        max_length=200,
        blank=True,
        default=""
    )
    LEVEL_CHOICES = [
        ('100', 'Level 100'),
        ('200', 'Level 200'),
        ('300', 'Level 300'),
        ('400', 'Level 400'),
        ('500', '5th Year'),
        ('600', '6th Year'),
    ]

    level = models.CharField(
        max_length=3,
        choices=LEVEL_CHOICES,
        blank=True,
        default='',
    )
    residential_area = models.CharField(max_length=200)
    zone = models.ForeignKey(
        Zone,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members'

    )
    registered_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    zone_confirmed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    user = models.OneToOneField(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='member_record'
    )
    def __str__(self):
        return self.full_name

class UserProfile(models.Model):
    ROLE_CHOICES = [
        ('chief_shepherd', 'Chief Shepherd'),
        ('zone_rep', 'Zone Representative'),
        ('scout', 'Scout'),
        ('shepherd', 'Shepherd'),
    ]
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='profile'
    )

    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='scout'
    )

    zone = models.ForeignKey(
        'Zone',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users'
    )

    def __str__(self):
        return f'{self.user.username} - {self.get_role_display()}'

class TransferRequest(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    member = models.ForeignKey(
        Member,
        on_delete=models.CASCADE,
        related_name='transfer_requests'
    )

    from_zone = models.ForeignKey(
        Zone,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='outgoing_transfers'
    )

    to_zone = models.ForeignKey(
        Zone,
        on_delete=models.PROTECT,
        related_name='incoming_transfers'
    )

    requested_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='submitted_transfers'
    )

    reason = models.TextField()

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending'
    )

    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_transfers'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    reviewed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f'{self.member.full_name} - {self.get_status_display()}'


class ShepherdingGroup(models.Model):
    shepherd = models.ForeignKey(
        Member,
        on_delete=models.PROTECT,
        related_name='shepherding_groups',
        limit_choices_to={'level__in': ['400', '500', '600']}
    )

    members = models.ManyToManyField(
        Member,
        related_name='shepherding_groups_as_member',
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.shepherd.full_name} - {self.shepherd.course}'

    def clean(self):
        from django.core.exceptions import ValidationError

        if self.shepherd.level not in ['400', '500', '600']:
            raise ValidationError(
                'Only Level 400, 5th Year, or 6th Year students can be shepherds.'
            )

        if not self.shepherd.course.strip():
            raise ValidationError(
                'The shepherd must have a registered course or programme.'
            )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def add_member(self, member):
        from django.core.exceptions import ValidationError

        if member.pk == self.shepherd.pk:
            raise ValidationError(
                'A shepherd cannot be a member of their own group.'
            )

        if member.course.strip().casefold() != self.shepherd.course.strip().casefold():
            raise ValidationError(
                'The student and shepherd must offer the same course or programme.'
            )

        if member.level not in ['100', '200', '300']:
            raise ValidationError(
                'Only Level 100, 200, or 300 students can be assigned as group members.'
            )

        if self.members.count() >= 4 and not self.members.filter(pk=member.pk).exists():
            raise ValidationError(
                'A shepherd cannot have more than four students.'
            )

        if ShepherdingGroup.objects.filter(members=member).exclude(pk=self.pk).exists():
            raise ValidationError(
                'This student is already assigned to another shepherding group.'
            )

        self.members.add(member)