from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db import transaction
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.generic import DeleteView
from invitations.forms import Invitation

from friends.models import Friends


@login_required
def friends(request):
    invited_friends = friends_invited_by_user(request.user)
    invited_by = friends_that_invited_user(request.user)
    if request.method == 'POST':
        if 'sub_invitation' in request.POST:
            send_invitation(request)
    else:
        return render(request, "friends.html", {'friends_list': invited_friends, 'invited_by': invited_by, })
    # return render(request, "profile.html", {'friends_list': friends_list, 'invited_by': invited_by, })
    return redirect("/accounts/friends/", {'friends_list': invited_friends, 'invited_by': invited_by, })


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


def friends_invited_by_user(owner):
    friends_with_status = []
    owners_invitations = Friends.objects.filter(library_owner=owner)
    for invitation in owners_invitations:
        if User.objects.filter(email=invitation.invited).exists():
            friend = User.objects.filter(email=invitation.invited).first()
            friends_with_status.append({'email': invitation.invited,
                                        'status': 'exists',
                                        'pk_in_group': invitation.pk,
                                        'username': friend.username,
                                        'pk_user': friend.pk})
        else:
            friends_with_status.append({'email': invitation.invited,
                                        'status': 'not exists',
                                        'pk_in_group': invitation.pk,
                                        'username': ""})
    return friends_with_status


def friends_that_invited_user(this_user):
    friends_with_status = []
    got_invitations = Friends.objects.filter(invited=this_user.email)
    for invitation in got_invitations:
        if User.objects.filter(email=invitation.library_owner.email).exists():
            friend = User.objects.filter(email=invitation.library_owner.email).first()
            friends_with_status.append({'email': invitation.library_owner.email,
                                        'status': 'exists',
                                        'pk_in_group': invitation.pk,
                                        'username': friend.username,
                                        'pk_user': friend.pk})
        else:
            friends_with_status.append({'email': invitation.library_owner.email,
                                        'status': 'not exists',
                                        'pk_in_group': invitation.pk,
                                        'username': ""})
    return friends_with_status


@transaction.atomic
def add_to_invited(owner, email):
    owners_invitations = Friends.objects.filter(library_owner=owner)
    found = owners_invitations.filter(invited=email).first()
    if found is None:
        new_in_group = Friends(library_owner=owner, invited=email)
        new_in_group.save()
    return


class FriendDelete(DeleteView):
    model = Friends
    template_name_suffix = '_delete_form'

    def get_success_url(self):
        return reverse('friends_url')
