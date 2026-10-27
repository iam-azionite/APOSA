from django.contrib import admin
from .models import Zone, Member, UserProfile, TransferRequest,ShepherdingGroup

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = (
        'full_name',
        'user',
        'phone_number',
        'course',
        'level',
        'residential_area',
        'zone',
        'zone_confirmed',
        'registered_by',
        'created_at',
    )

    list_filter = (
        'zone',
        'zone_confirmed',
        'level',
        'course',
    )

    search_fields = (
        'full_name',
        'phone_number',
        'residential_area',
        'course',
        'user__username',
        'user__email',
        'zone__name',
        'registered_by__username',
    )

    list_editable = ('zone_confirmed',)
    list_per_page = 25
    ordering = ('full_name',)

    readonly_fields = ('created_at',)
