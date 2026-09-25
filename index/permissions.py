from rest_framework.permissions import BasePermission

class IsATMOrOnlyRead(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        else:
            return request.user.is_ATM or request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        if request.method == 'GET':
            return True
        else:
            return request.user.is_ATM or request.user.is_superuser

class IsPostmasterOrOnlyRead(BasePermission):
    def has_permission(self, request, view):
        if request.method == 'GET':
            return True
        else:
            return request.user.is_postmaster or request.user.is_superuser

    def has_object_permission(self, request, view, obj):
        if request.method == 'GET':
            return True
        else:
            return request.user.is_postmaster or request.user.is_superuser