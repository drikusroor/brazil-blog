import json
from rest_framework import viewsets
from rest_framework import serializers
from django.utils import timezone
from .models import DrinkConsumption, DrinkType
from locations.models import ItineraryStop
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import permission_classes, action
from rest_framework.response import Response
from django.db.models import Sum
from django.views.generic import TemplateView
from django.db.models import Count, Avg
from django.db.models.functions import TruncDate
from django.core.serializers.json import DjangoJSONEncoder

from django.contrib.auth.models import User

from blog.templatetags.user_tags import user_display_name
from blog.serializers import UserSerializer


class DrinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DrinkConsumption
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["user"] = user_display_name(instance.consumer)

        return data


class CustomJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, timezone.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        return super().default(obj)


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

    # get drinks/count{?type=}
    @action(detail=False, methods=["get"])
    def get_drinks_count(self, request):
        drinks_type = request.query_params.get("drink_type")

        if drinks_type:
            # count times amount field
            count = DrinkConsumption.objects.filter(drink_type=drinks_type).aggregate(
                count=Sum("amount")
            )

            return Response({"count": count})

        count = DrinkConsumption.objects.aggregate(count=Sum("amount"))
        return Response({"count": count})

    # get total amount per type
    @action(detail=False, methods=["get"])
    def get_total_amount_per_type(self, request):
        total_amount_per_type = (
            DrinkConsumption.objects.values("drink_type")
            .annotate(total_amount=Sum("amount"))
            .order_by("drink_type")
        )

        return Response(total_amount_per_type)

    @action(detail=False, methods=["post"])
    def quick_add_drink(self, request):
        drink_type_id = request.data.get("drink_type")
        amount = request.data.get("amount", 1)
        location = request.data.get("location", "")

        DrinkConsumption.objects.create(
            consumer=request.user, drink_type_id=drink_type_id, amount=amount
        )

        # find ItineraryStop whose start_date is less than or equal to current date
        # and end_date is greater than or equal to current date
        if not location:
            stop = ItineraryStop.objects.filter(
                itinerary__stops__start_date__lte=timezone.now(),
                itinerary__stops__end_date__gte=timezone.now(),
                itinerary__stops__location__isnull=False,
            ).first()
            if stop:
                location = stop.location

        return Response({"status": "success"})


class DrinkStatisticsView(TemplateView):
    template_name = "statistics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Drinks per user with complete user data
        drinks_per_user = (
            User.objects.filter(drink_consumptions__gt=0)
            .annotate(
                total_drinks=Sum("drink_consumptions__amount"),
                total_days=Count("drink_consumptions__date", distinct=True),
            )
            .order_by("-total_drinks")
        )

        context["drinks_per_user"] = drinks_per_user

        # Drinks per drink type
        context["drinks_per_type"] = DrinkType.objects.annotate(
            total=Sum("drink_consumptions__amount")
        ).order_by("-total")

        # Drinks per day (for the chart)
        drinks_per_day = (
            DrinkConsumption.objects.annotate(date_day=TruncDate("date"))
            .values("date_day", "drink_type__name")
            .annotate(total=Sum("amount"))
            .order_by("date_day")
        )
        context["drinks_per_day"] = json.dumps(
            list(drinks_per_day), cls=CustomJSONEncoder
        )

        # Drinks with location for the map
        drinks_with_location = list(
            DrinkConsumption.objects.exclude(location="").values(
                "location", "amount", "drink_type__name"
            )
        )
        context["drinks_with_location"] = json.dumps(
            drinks_with_location, cls=CustomJSONEncoder
        )

        # Average drinks per day per type
        avg_drinks = (
            DrinkConsumption.objects.values("drink_type__name")
            .annotate(avg_amount=Avg("amount"), total_days=Count("date", distinct=True))
            .annotate(avg_per_day=Sum("amount") / Count("date", distinct=True))
            .order_by("-avg_per_day")
        )
        context["avg_drinks_per_day"] = list(avg_drinks)

        return context
