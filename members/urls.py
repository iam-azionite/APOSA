
from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),

    path('members/', views.member_list, name='member_list'),

    path(
        'members/register/',
        views.register_member,
        name='register_member'
    ),

    path(
        'members/<int:member_id>/transfer/',
        views.request_transfer,
        name='request_transfer'
    ),

    path(
        'members/<int:member_id>/confirm/',
        views.confirm_member,
        name='confirm_member'
    ),

    path(
        'transfers/',
        views.transfer_requests,
        name='transfer_requests'
    ),

    path(
        'transfers/<int:transfer_id>/review/',
        views.review_transfer,
        name='review_transfer'
    ),
path(
    'aposa-dashboard/',
    views.aposa_admin_dashboard,
    name='aposa_admin_dashboard',
),
path(
    'shepherding/',
    views.shepherding_management,
    name='shepherding_management'
),
path(
    'my-shepherding/',
    views.shepherd_dashboard,
    name='shepherd_dashboard',
),

]
