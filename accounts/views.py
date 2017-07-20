from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import DeleteView
from invitations.forms import Invitation

from accounts.models import InGroup


@login_required
def profile(request):
    friends_list = friends(request.user)
    if request.method == 'POST':
        if 'sub_invitation' in request.POST:
            send_invitation(request)
    else:
        return render(request, "profile.html", {'friends_list': friends_list, })
    # return render(request, "profile.html", {'friends_list': friends_list, })
    return redirect("/accounts/profile/", {'friends_list': friends_list, })


def send_invitation(request):
    email_value = request.POST['email_value']
    try:
        invite = Invitation.create(email_value, inviter=request.user)
        invite.save()
        invite.send_invitation(request)
        add_to_invited(request.user, email_value)
    except Exception:
        messages.add_message(request, messages.WARNING, 'Problem occurred when sending invitation.')
        return
    messages.add_message(request, messages.SUCCESS, 'Invitation was sent.')
    return


def friends(owner):
    friends_with_status = []
    owners_invitations = InGroup.objects.filter(library_owner=owner)
    for invitations in owners_invitations:
        if User.objects.filter(email=invitations.invited).exists():
            friends_with_status.append({'email': invitations.invited, 'status': 'exists'})
        else:
            friends_with_status.append({'email': invitations.invited, 'status': 'not_exists'})
    return friends_with_status


@transaction.atomic
def add_to_invited(owner, email):
    owners_invitations = InGroup.objects.filter(library_owner=owner)
    found = owners_invitations.filter(invited=email).first()
    if found is None:
        new_in_group = InGroup(library_owner=owner, invited=email)
        new_in_group.save()
    return


# class InGroupDelete(DeleteView):
#     model = InGroup
#     template_name_suffix = '_delete_form'
#
#     def get_success_url(self):
#         return reverse('users_books_url')
