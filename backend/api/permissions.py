from rest_framework import permissions


# class IsAdminAuthorOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
#     message = "Доступ запрещен!"

#     def has_object_permission(self, request, view, obj):
#         return (
#             request.method in permissions.SAFE_METHODS
#             or request.user.is_superuser
#             or obj.author == request.user
#         )


class IsAuthorOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    message = 'Редактирование не доступно.'

    def has_object_permission(self, request, view, obj):
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user
                or request.user.is_superuser)

