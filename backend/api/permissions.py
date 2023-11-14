from rest_framework import permissions


# class IsAdminAuthorOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
#     message = "Доступ запрещен!"

#     def has_object_permission(self, request, view, obj):
#         return (
#             request.method in permissions.SAFE_METHODS
#             or request.user.is_superuser
#             or obj.author == request.user
#         )
# class IsAdminOrReadOnly(permissions.BasePermission):
#     """Права доступа для админа."""
#     def has_permission(self, request, view):
#         if request.method in permissions.SAFE_METHODS:
#             return True
#         return bool(request.user and request.user.is_superuser)

class IsAuthorOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    message = 'Редактирование не доступно.'

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user
                or request.user.is_superuser)
