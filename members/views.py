from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render, redirect,get_object_or_404
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from .models import Member, Zone, UserProfile, TransferRequest,ShepherdingGroup
from .forms import MemberForm
from django.http import HttpResponseForbidden
from django.utils import timezone
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.core.exceptions import ValidationError


def get_user_profile(user):
    profile, created = UserProfile.objects.get_or_create(
    user=user,
    defaults={'role': 'scout'}
    )
    return profile

@login_required
def dashboard(request):
    profile = get_user_profile(request.user)

    # CHIEF SHEPHERD DASHBOARD
    if profile.role == 'chief_shepherd':
        members = Member.objects.all()
        zones = Zone.objects.all()

        # Prepare zone information without using zone.member_set
        zone_data = [
            {
                'zone': zone,
                'member_count': Member.objects.filter(zone=zone).count(),
            }
            for zone in zones
        ]

        context = {
            'role': profile.role,
            'total_members': members.count(),
            'total_zones': zones.count(),

            'unassigned_members': members.filter(
                zone__isnull=True
            ).count(),

            'confirmed_members': members.filter(
                zone_confirmed=True
            ).count(),

            'unconfirmed_members': members.filter(
                zone_confirmed=False
            ).count(),

            'pending_transfers': TransferRequest.objects.filter(
                status='pending'
            ).count(),

            'zones': zones,
            'zone_data': zone_data,

            # Data for the membership chart
            'zone_labels': [zone.name for zone in zones],
            'zone_member_counts': [
                item['member_count'] for item in zone_data
            ],
        }

    # ZONE REPRESENTATIVE DASHBOARD
    elif profile.role == 'zone_rep':
        if profile.zone:
            members = Member.objects.filter(zone=profile.zone)
            zones = [profile.zone]

            zone_data = [{
                'zone': profile.zone,
                'member_count': members.count(),
            }]
        else:
            members = Member.objects.none()
            zones = []
            zone_data = []

        context = {
            'role': profile.role,
            'total_members': members.count(),
            'total_zones': len(zones),

            'unassigned_members': members.filter(
                zone__isnull=True
            ).count(),

            'confirmed_members': members.filter(
                zone_confirmed=True
            ).count(),

            'unconfirmed_members': members.filter(
                zone_confirmed=False
            ).count(),

            'zones': zones,
            'zone_data': zone_data,
        }

    # SCOUT DASHBOARD
    else:
        members = Member.objects.filter(
            registered_by=request.user
        )

        context = {
            'role': profile.role,
            'total_members': members.count(),
            'total_zones': 0,

            'unassigned_members': members.filter(
                zone__isnull=True
            ).count(),

            'confirmed_members': members.filter(
                zone_confirmed=True
            ).count(),

            'unconfirmed_members': members.filter(
                zone_confirmed=False
            ).count(),

            'zones': [],
            'zone_data': [],
        }

    return render(request, 'dashboard.html', context)

@login_required
def register_member(request):
    profile = get_user_profile(request.user)

    if request.method == 'POST':
        form = MemberForm(request.POST)
    else:
        form = MemberForm()

    # Scouts cannot select or assign a zone.
    if profile.role == 'scout':
        form.fields.pop('zone', None)

    # Zone representatives can only select their own zone.
    elif profile.role == 'zone_rep':
        if profile.zone:
            form.fields['zone'].queryset = Zone.objects.filter(
                id=profile.zone_id
            )
        else:
            form.fields['zone'].queryset = Zone.objects.none()

    if request.method == 'POST' and form.is_valid():
        member = form.save(commit=False)
        member.registered_by = request.user

        if profile.role == 'scout':
            member.zone = None
            member.zone_confirmed = False

        elif profile.role == 'zone_rep':
            if not profile.zone:
                return render(request, 'register_member.html', {
                    'form': form,
                    'error': 'Your account has no assigned zone.'
                })

            member.zone = profile.zone
            member.zone_confirmed = True

        elif profile.role == 'chief_shepherd':
            member.zone_confirmed = member.zone is not None

        member.save()
        return redirect('member_list')

    return render(request, 'register_member.html', {
        'form': form
    })

@login_required
def member_list(request):
    profile = get_user_profile(request.user)
    # Restrict members according to the user's role.
    if profile.role == 'chief_shepherd':
        members = Member.objects.select_related('zone').all()

    elif profile.role == 'zone_rep':
        members = Member.objects.select_related('zone').filter(
            zone=profile.zone
        )

    else:
        members = Member.objects.select_related('zone').filter(
            registered_by=request.user
        )

    search = request.GET.get('search', '').strip()

    if search:
        members = members.filter(
            Q(full_name__icontains=search)
            | Q(phone_number__icontains=search)
            | Q(residential_area__icontains=search)
        )

    return render(request, 'member_list.html', {
        'members': members,
        'search': search,
        'role': profile.role,
    })


@login_required
def request_transfer(request, member_id):
    profile, _ = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'role': 'scout'}
    )

    # Only the Chief Shepherd and Zone Representatives may request transfers
    if profile.role not in ['chief_shepherd', 'zone_rep']:
        return HttpResponseForbidden(
            'You are not authorized to request transfers.'
        )

    member = get_object_or_404(Member, id=member_id)

    # A representative can transfer only members in their assigned zone
    if profile.role == 'zone_rep':
        if not profile.zone or member.zone_id != profile.zone_id:
            return HttpResponseForbidden(
                'You can only request transfers for members in your zone.'
            )

    zones = Zone.objects.exclude(id=member.zone_id)

    if request.method == 'POST':
        to_zone_id = request.POST.get('to_zone')
        reason = request.POST.get('reason', '').strip()

        to_zone = get_object_or_404(zones, id=to_zone_id)

        if not reason:
            return render(request, 'request_transfer.html', {
                'member': member,
                'zones': zones,
                'error': 'Please provide a reason for the transfer.'
            })

        # Prevent multiple pending requests for the same member
        pending_exists = TransferRequest.objects.filter(
            member=member,
            status='pending'
        ).exists()

        if pending_exists:
            return render(request, 'request_transfer.html', {
                'member': member,
                'zones': zones,
                'error': 'This member already has a pending transfer request.'
            })

        TransferRequest.objects.create(
            member=member,
            from_zone=member.zone,
            to_zone=to_zone,
            requested_by=request.user,
            reason=reason
        )

        return redirect('transfer_requests')

    return render(request, 'request_transfer.html', {
        'member': member,
        'zones': zones
    })

@login_required
def transfer_requests(request):
    profile, _ = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'role': 'scout'}
    )

    if profile.role == 'chief_shepherd':
        transfers = TransferRequest.objects.select_related(
            'member', 'from_zone', 'to_zone', 'requested_by'
        ).order_by('-created_at')

    elif profile.role == 'zone_rep':
        transfers = TransferRequest.objects.filter(
            requested_by=request.user
        ).select_related(
            'member', 'from_zone', 'to_zone'
        ).order_by('-created_at')

    else:
        return HttpResponseForbidden(
            'You are not authorized to view transfer requests.'
        )

    return render(request, 'transfer_requests.html', {
        'transfers': transfers,
        'role': profile.role
    })

@login_required
def review_transfer(request, transfer_id):
    if request.method != 'POST':
        return redirect('transfer_requests')

    profile, _ = UserProfile.objects.get_or_create(
        user=request.user,
        defaults={'role': 'scout'}
    )

    if profile.role != 'chief_shepherd':
        return HttpResponseForbidden(
            'Only the Chief Shepherd can review transfer requests.'
        )

    transfer = get_object_or_404(
        TransferRequest.objects.select_related('member'),
        id=transfer_id
    )

    if transfer.status != 'pending':
        return redirect('transfer_requests')

    action = request.POST.get('action')

    if action == 'approve':
        # Ensure the member has not changed zones since the request
        if transfer.member.zone_id != transfer.from_zone_id:
            transfer.status = 'rejected'
            transfer.reviewed_by = request.user
            transfer.reviewed_at = timezone.now()
            transfer.save()
            return redirect('transfer_requests')

        transfer.member.zone = transfer.to_zone
        transfer.member.zone_confirmed = True
        transfer.member.save()

        transfer.status = 'approved'

    elif action == 'reject':
        transfer.status = 'rejected'

    else:
        return HttpResponseForbidden('Invalid action.')

    transfer.reviewed_by = request.user
    transfer.reviewed_at = timezone.now()
    transfer.save()

    return redirect('transfer_requests')


@login_required
@require_POST
def confirm_member(request, member_id):
    profile = get_user_profile(request.user)

    # Only the Chief Shepherd can confirm members
    if profile.role != 'chief_shepherd':
        return HttpResponseForbidden(
            "Only the Chief Shepherd can confirm members."
        )

    member = get_object_or_404(Member, id=member_id)

    # Confirm the member's zone
    member.zone_confirmed = True
    member.save(update_fields=['zone_confirmed'])

    return redirect('member_list')

@staff_member_required
def aposa_admin_dashboard(request):
    total_members = Member.objects.count()
    total_zones = Zone.objects.count()

    confirmed_members = Member.objects.filter(
        zone_confirmed=True
    ).count()

    pending_transfers = TransferRequest.objects.filter(
        status='pending'
    ).count()

    recent_members = Member.objects.select_related(
        'zone'
    ).order_by('-created_at')[:5]

    recent_transfers = TransferRequest.objects.select_related(
        'member',
        'from_zone',
        'to_zone',
    ).filter(
        status='pending'
    ).order_by('-created_at')[:5]

    context = {
        'total_members': total_members,
        'total_zones': total_zones,
        'confirmed_members': confirmed_members,
        'pending_transfers': pending_transfers,
        'recent_members': recent_members,
        'recent_transfers': recent_transfers,
    }

    return render(
        request,
        'admin_dashboard.html',
        context,
    )


# ==========================================
# SHEPHERDING MANAGEMENT
# ==========================================

@login_required
def shepherding_management(request):
    profile = get_user_profile(request.user)

    # Only the Chief Shepherd can manage shepherding groups.
    if profile.role != 'chief_shepherd':
        return HttpResponseForbidden(
            "Only the Chief Shepherd can manage shepherding groups."
        )

    groups = ShepherdingGroup.objects.select_related(
        'shepherd'
    ).prefetch_related(
        'members'
    ).order_by('shepherd__course', 'shepherd__full_name')

    # Eligible shepherds must be Level 400, 5th Year, or 6th Year.
    shepherds = Member.objects.filter(
        level__in=['400', '500', '600']
    ).exclude(
        course=''
    ).order_by('course', 'full_name')

    # Students eligible to be assigned to a group.
    assigned_ids = ShepherdingGroup.objects.values_list(
        'members__id',
        flat=True
    )

    unassigned_students = Member.objects.filter(
        level__in=['100', '200', '300']
    ).exclude(
        course=''
    ).exclude(
        id__in=assigned_ids
    ).order_by('course', 'level', 'full_name')

    if request.method == 'POST':
        action = request.POST.get('action')

        # Create a shepherding group.
        if action == 'create_group':
            shepherd_id = request.POST.get('shepherd')

            shepherd = get_object_or_404(
                shepherds,
                id=shepherd_id
            )

            if ShepherdingGroup.objects.filter(
                shepherd=shepherd
            ).exists():
                messages.error(
                    request,
                    'This student already has a shepherding group.'
                )
            else:
                ShepherdingGroup.objects.create(
                    shepherd=shepherd
                )

                messages.success(
                    request,
                    f'A shepherding group has been created for {shepherd.full_name}.'
                )

            return redirect('shepherding_management')

        # Assign a student to a shepherd.
        elif action == 'assign_student':
            group_id = request.POST.get('group')
            student_id = request.POST.get('student')

            group = get_object_or_404(
                ShepherdingGroup.objects.select_related('shepherd'),
                id=group_id
            )

            student = get_object_or_404(
                Member,
                id=student_id,
                level__in=['100', '200', '300']
            )

            try:
                group.add_member(student)

                messages.success(
                    request,
                    f'{student.full_name} has been assigned to {group.shepherd.full_name}.'
                )

            except ValidationError as error:
                messages.error(
                    request,
                    ' '.join(error.messages)
                )

            return redirect('shepherding_management')

        # Remove a student from a group.
        elif action == 'remove_student':
            group_id = request.POST.get('group')
            student_id = request.POST.get('student')

            group = get_object_or_404(
                ShepherdingGroup,
                id=group_id
            )

            student = get_object_or_404(
                group.members,
                id=student_id
            )

            group.members.remove(student)

            messages.success(
                request,
                f'{student.full_name} has been removed from the group.'
            )

            return redirect('shepherding_management')

        else:
            return HttpResponseForbidden('Invalid action.')

    context = {
        'groups': groups,
        'shepherds': shepherds,
        'unassigned_students': unassigned_students,
    }

    return render(
        request,
        'members/shepherding_management.html',
        context
    )


# ==========================================
# SHEPHERD DASHBOARD
# ==========================================

@login_required
def shepherding_management(request):
    profile = get_user_profile(request.user)

    # Only the Chief Shepherd can manage shepherding groups.
    if profile.role != 'chief_shepherd':
        return HttpResponseForbidden(
            "You are not permitted to manage shepherding groups."
        )

    if request.method == 'POST':
        action = request.POST.get('action')

        # Create a shepherding group.
        if action == 'create_group':
            shepherd_id = request.POST.get('shepherd')

            shepherd = get_object_or_404(
                Member,
                id=shepherd_id
            )

            try:
                group = ShepherdingGroup.objects.create(
                    shepherd=shepherd
                )

                messages.success(
                    request,
                    f"Shepherding group for {shepherd.full_name} created successfully."
                )

            except ValidationError as error:
                messages.error(request, ' '.join(error.messages))

        # Assign a student to a shepherd.
        elif action == 'assign_student':
            group_id = request.POST.get('group')
            student_id = request.POST.get('student')

            group = get_object_or_404(
                ShepherdingGroup,
                id=group_id
            )

            student = get_object_or_404(
                Member,
                id=student_id
            )

            try:
                group.add_member(student)

                messages.success(
                    request,
                    f"{student.full_name} has been assigned successfully."
                )

            except ValidationError as error:
                messages.error(request, ' '.join(error.messages))

        # Remove a student from a group.
        elif action == 'remove_student':
            group_id = request.POST.get('group')
            student_id = request.POST.get('student')

            group = get_object_or_404(
                ShepherdingGroup,
                id=group_id
            )

            student = get_object_or_404(
                Member,
                id=student_id
            )

            group.members.remove(student)

            messages.success(
                request,
                f"{student.full_name} has been removed from the group."
            )

        return redirect('shepherding_management')

    groups = ShepherdingGroup.objects.select_related(
        'shepherd'
    ).prefetch_related('members').order_by('shepherd__full_name')

    shepherds = Member.objects.filter(
        level__in=['400', '500', '600'],
        course__gt=''
    ).order_by('full_name')

    students = Member.objects.filter(
        level__in=['100', '200', '300'],
        course__gt=''
    ).order_by('full_name')

    context = {
        'role': profile.role,
        'page': 'shepherding',
        'groups': groups,
        'shepherds': shepherds,
        'students': students,
        'total_groups': groups.count(),
    }

    return render(request, 'dashboard.html', context)


@login_required
def shepherd_dashboard(request):
    profile = get_user_profile(request.user)

    # Only users with the shepherd role can access this page.
    if profile.role != 'shepherd':
        return HttpResponseForbidden(
            "You are not authorized to access the shepherd dashboard."
        )

    # Find the member record linked to the logged-in shepherd.
    try:
        shepherd_member = request.user.member_record
    except Member.DoesNotExist:
        return render(
            request,
            'dashboard.html',
            {
                'role': 'shepherd',
                'page': 'shepherd_dashboard',
                'error_message': (
                    'Your login account has not been linked to your '
                    'member record. Please contact the Chief Shepherd.'
                ),
                'groups': [],
                'students': [],
                'total_students': 0,
            },
        )

    # Find the shepherd's group.
    group = ShepherdingGroup.objects.filter(
        shepherd=shepherd_member
    ).first()

    if group is None:
        return render(
            request,
            'dashboard.html',
            {
                'role': 'shepherd',
                'page': 'shepherd_dashboard',
                'group': None,
                'groups': [],
                'students': [],
                'total_students': 0,
                'error_message': (
                    'You do not have a shepherding group yet. '
                    'Please contact the Chief Shepherd.'
                ),
            },
        )

    # Retrieve only students assigned to this shepherd's group.
    students = group.members.all().order_by('full_name')

    return render(
        request,
        'dashboard.html',
        {
            'role': 'shepherd',
            'page': 'shepherd_dashboard',
            'group': group,
            'groups': [group],
            'students': students,
            'total_students': students.count(),
        },
    )