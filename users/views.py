from rest_framework import generics
from rest_framework.permissions import AllowAny

from users.serializers import UserSerializer


class UserCreateAPIView(generics.CreateAPIView):
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    def perform_create(self, serializer):
        user = serializer.save()
        user.set_password(serializer.validated_data.get("password"))
        user.is_active = True
        user.save()
