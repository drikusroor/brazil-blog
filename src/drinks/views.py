from rest_framework import viewsets
from rest_framework import serializers
from .models import DrinkConsumption
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import permission_classes

from blog.templatetags.user_tags import user_display_name


class DrinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DrinkConsumption
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["user"] = user_display_name(instance.consumer)

        return data


# Create your views here.
class DrinkViewSet(viewsets.ModelViewSet):
    queryset = DrinkConsumption.objects.all()
    serializer_class = DrinkSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned drinks to a given user,
        by filtering against a `user` query parameter in the URL.
        """
        queryset = super().get_queryset()
        user_id = self.request.query_params.get("user")
        if user_id is not None:
            queryset = queryset.filter(consumer_id=user_id)
        return queryset

    @permission_classes([IsAuthenticated, IsAdminUser])
    def perform_create(self, serializer):
        serializer.save(consumer=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context
