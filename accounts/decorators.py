from django.contrib.auth.models import User
from django.http import HttpResponseForbidden

from accounts.models import InGroup


def is_friend():
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            try:
                this_user = request.user
                friends_list = InGroup.objects.filter(library_owner=this_user)
                friend_fd = kwargs.get('pk_user', '')
                friend = User.objects.get(id=friend_fd)
                if this_user == friend:
                    return func(request, *args, **kwargs)
                for elem in friends_list:
                    if elem.invited == friend.email:
                        return func(request, *args, **kwargs)
            except:
                return HttpResponseForbidden()
            return HttpResponseForbidden()
        return wrapper
    return decorator



