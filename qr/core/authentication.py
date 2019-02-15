from rest_framework.authentication import TokenAuthentication, get_authorization_header
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import authentication
from rest_framework import exceptions
import datetime
from django.utils.translation import ugettext_lazy as _
import inspect
import pytz
from django.utils import timezone
from collections import Counter
from rest_framework.throttling import SimpleRateThrottle
from django.contrib.auth.models import User

class ExpiringTokenAuthentication(TokenAuthentication):
    """ Modulo en construccion """
    def authenticate_credentials(self, key):
        print("#########################################")
        print(key)
        print("sdfdsfsgfhgthjhjfhjhfdhdhsgadgfsghhggjjh")
        print("##########################################")

        model = self.get_model()

        print(model)
        #token = model.objects.get(key=key)
        #print(token)
        try:
            token = model.objects.select_related('user').get(key=key)
        except model.DoesNotExist:
            raise exceptions.AuthenticationFailed(_('Invalid token.'))

        if not token.user.is_active:
            raise exceptions.AuthenticationFailed(_('User inactive or deleted.'))

        # This is required for the time comparison
        utc_now = datetime.datetime.utcnow()
        print("utcnow", utc_now)
        utc_now = utc_now.replace(tzinfo=pytz.utc)

        print(33333333333333333333333333333333333)
        print("timezone.now()", timezone.now())
        print("utcnow 2", utc_now)
        print("token created", token.created)
        print(token.created < utc_now - datetime.timedelta(hours=1))
        print(utc_now - datetime.timedelta(hours=1))

        if token.created < utc_now - datetime.timedelta(hours=24):
            print("hooooosddfsdfgfgggggggggggggggggggggggggggg")
            raise exceptions.AuthenticationFailed(_('Token has expired'))

        return (token.user, token)



class UserLoginRateThrottle(SimpleRateThrottle):
    """esta clase previene ataques de fuerza bruta"""
    scope = 'loginAttempts'

    def get_cache_key(self, request, view):
        print("get_cache_key")
        user = User.objects.filter(username=request.data.get('username'))
        ident = user[0].pk if user else self.get_ident(request)

        return self.cache_format % {
            'scope': self.scope,
            'ident': ident
        }

    def allow_request(self, request, view):
        """
        Implement the check to see if the request should be throttled.
        On success calls `throttle_success`.
        On failure calls `throttle_failure`.
        """
        
        if self.rate is None:
            return True

        self.key = self.get_cache_key(request, view)
        print("self.key", self.key)
        if self.key is None:
            return True

        self.history = self.cache.get(self.key, [])

        self.now = self.timer()

        while self.history and self.history[-1] <= self.now - self.duration:
            self.history.pop()
        if len(self.history) >= self.num_requests:
            return self.throttle_failure()

        return self.throttle_success(request)

    def throttle_success(self, request):
        print("throttle_success")
        """
        Inserts the current request's timestamp along with the key
        into the cache.
        """
        user = User.objects.filter(username=request.data.get('username'))
        if user:
            self.history.insert(0, user[0].id)
        self.history.insert(0, self.now)
        self.cache.set(self.key, self.history, self.duration)
        return True
