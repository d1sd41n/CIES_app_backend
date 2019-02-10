from rest_framework.permissions import BasePermission
from core.models import CustomUser
# print(view.kwargs)

class DeveloperOnly(BasePermission):
    def has_permission(self, request, view):
        return  "Developer" in request.user.groups.values_list('name',flat=True)


class ManagerAndSuperiorsOnly(BasePermission):
    def has_permission(self, request, view):
        if  "Developer" in request.user.groups.values_list('name',flat=True):
            return True
        user_company = str(CustomUser.objects.get(user=request.user).seat.company.id)
        company_pk = view.kwargs['company_pk']
        return user_company == company_pk and "Manager" in request.user.groups.values_list('name',flat=True)


class ManagerAndSuperiorsOnly(BasePermission):
    def has_permission(self, request, view):
        if  "Developer" in request.user.groups.values_list('name',flat=True):
            return True
        user_company = str(CustomUser.objects.get(user=request.user).seat.company.id)
        company_pk = view.kwargs['company_pk']
        return user_company == company_pk and "Manager" in request.user.groups.values_list('name',flat=True)


class SupervisorAndSuperiorsOnly(BasePermission):
    def has_permission(self, request, view):
        if  "Developer" in request.user.groups.values_list('name',flat=True):
            return True
        user_company = str(CustomUser.objects.get(user=request.user).seat.company.id)
        company_pk = view.kwargs['company_pk']
        if user_company != company_pk:
            return False
        if "Manager" in request.user.groups.values_list('name',flat=True):
            return True
        user_seat = str(CustomUser.objects.get(user=request.user).seat.id)
        seat_pk = view.kwargs['seat_pk']
        if user_seat != seat_pk:
            return False
        return "Supervisor" in request.user.groups.values_list('name',flat=True)


class GuardAndSuperiorsOnly(BasePermission):
    def has_permission(self, request, view):
        if  "Developer" in request.user.groups.values_list('name',flat=True):
            return True
        user_company = str(CustomUser.objects.get(user=request.user).seat.company.id)
        company_pk = view.kwargs['company_pk']
        if user_company != company_pk:
            return False
        if "Manager" in request.user.groups.values_list('name',flat=True):
            return True
        user_seat = str(CustomUser.objects.get(user=request.user).seat.id)
        seat_pk = view.kwargs['seat_pk']
        if user_seat != seat_pk:
            return False
        if "Supervisor" in request.user.groups.values_list('name',flat=True):
            return True
        return "Guard" in request.user.groups.values_list('name',flat=True)
