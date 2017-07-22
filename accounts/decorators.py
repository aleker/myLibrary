from django.contrib.auth.models import User
from django.http import HttpResponseForbidden

from friends.models import Friends


def is_friend():
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            try:
                this_user = request.user
                users_that_invited_this_user = Friends.objects.filter(invited=this_user.email)
                pk_of_friend_this_user_wants_to_visit = kwargs.get('pk_user', '')
                friend_this_user_wants_to_visit = User.objects.get(id=pk_of_friend_this_user_wants_to_visit)
                if this_user == friend_this_user_wants_to_visit:
                    return func(request, *args, **kwargs)
                for elem in users_that_invited_this_user:
                    if elem.library_owner == friend_this_user_wants_to_visit:
                        return func(request, *args, **kwargs)
            except:
                return HttpResponseForbidden()
            return HttpResponseForbidden()
        return wrapper
    return decorator


def is_friend2(function):
    def wrapper(request, *args, **kwargs):
        try:
            this_user = request.user
            users_that_invited_this_user = Friends.objects.filter(invited=this_user.email)
            pk_of_friend_this_user_wants_to_visit = kwargs.get('pk_user', '')
            friend_this_user_wants_to_visit = User.objects.get(id=pk_of_friend_this_user_wants_to_visit)
            if this_user == friend_this_user_wants_to_visit:
                return function(request, *args, **kwargs)
            for elem in users_that_invited_this_user:
                if elem.library_owner == friend_this_user_wants_to_visit:
                    return function(request, *args, **kwargs)
        except:
            return HttpResponseForbidden()
        return HttpResponseForbidden()

    wrapper.__doc__ = function.__doc__
    wrapper.__name__ = function.__name__
    return wrapper


def is_me():
    def decorator(func):
        def wrapper(request, *args, **kwargs):
            try:
                this_user = request.user
                pk_of_friend_this_user_wants_to_visit = kwargs.get('pk_user', '')
                friend_this_user_wants_to_visit = User.objects.get(id=pk_of_friend_this_user_wants_to_visit)
                if this_user == friend_this_user_wants_to_visit:
                    return func(request, *args, **kwargs)
            except:
                return HttpResponseForbidden()
            return HttpResponseForbidden()
        return wrapper
    return decorator


def is_me2(function):
    def wrapper(request, *args, **kwargs):
        try:
            this_user = request.user
            pk_of_friend_this_user_wants_to_visit = kwargs.get('pk_user', '')
            friend_this_user_wants_to_visit = User.objects.get(id=pk_of_friend_this_user_wants_to_visit)
            if this_user == friend_this_user_wants_to_visit:
                return function(request, *args, **kwargs)
        except:
            return HttpResponseForbidden()
        return HttpResponseForbidden()
    return wrapper

