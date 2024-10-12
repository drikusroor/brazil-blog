import json
from datetime import date
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
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.core.serializers.json import DjangoJSONEncoder

from django.contrib.auth.models import User

from blog.templatetags.user_tags import user_display_name


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

        DrinkConsumption.objects.create(
            consumer=request.user,
            drink_type_id=drink_type_id,
            amount=amount,
            location=location,
        )

        return Response({"status": "success"})


class DrinkStatisticsView(TemplateView):
    template_name = "drinks-statistics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        # Drinks per user with complete user data and drink type breakdown
        drinks_per_user = (
            User.objects.filter(drink_consumptions__isnull=False)
            .distinct()
            .annotate(
                total_drinks=Sum("drink_consumptions__amount"),
                total_days=Count("drink_consumptions__date", distinct=True),
            )
            .order_by("-total_drinks")
        )

        # Get drink type breakdown for each user
        drink_types = DrinkType.objects.all()
        for user in drinks_per_user:
            user.drink_breakdown = []
            for drink_type in drink_types:
                amount = (
                    DrinkConsumption.objects.filter(
                        consumer=user, drink_type=drink_type
                    ).aggregate(total=Sum("amount"))["total"]
                    or 0
                )
                if amount > 0:
                    user.drink_breakdown.append(
                        {
                            "name": drink_type.name,
                            "amount": amount,
                            "image": drink_type.image,
                        }
                    )
            user.drink_breakdown.sort(key=lambda x: x["amount"], reverse=True)

        context["drinks_per_user"] = drinks_per_user

        # Drinks per drink type
        drinks_per_type = (
            DrinkType.objects.filter(drink_consumptions__isnull=False)
            .distinct()
            .annotate(
                total_drinks=Sum("drink_consumptions__amount"),
                total_days=Count("drink_consumptions__date", distinct=True),
            )
            .order_by("-total_drinks")
        )

        # Get user breakdown for each drink type
        users = User.objects.all()
        for drink_type in drinks_per_type:
            drink_type.drink_breakdown = []
            for user in users:
                amount = (
                    DrinkConsumption.objects.filter(
                        consumer=user, drink_type=drink_type
                    ).aggregate(total=Sum("amount"))["total"]
                    or 0
                )
                if amount > 0:
                    drink_type.drink_breakdown.append(
                        {
                            "name": user_display_name(user),
                            "amount": amount,
                            "user": user,
                        }
                    )
            drink_type.drink_breakdown.sort(key=lambda x: x["amount"], reverse=True)

        context["drinks_per_type"] = drinks_per_type

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
        # including drink type's image url
        drinks_with_location = list(
            DrinkConsumption.objects.exclude(location="").values(
                "location", "amount", "drink_type__name", "drink_type__image__file"
            )
        )
        context["drinks_with_location"] = json.dumps(
            drinks_with_location, cls=CustomJSONEncoder
        )

        # TODO: Improve this by basing the amount of days on the first consumption's day
        # old_start_date = ItineraryStop.objects.order_by("start_date").first().start_date
        start_date = (
            DrinkConsumption.objects.order_by("date")
            .annotate(date_day=TruncDate("date"))
            .first()
            .date_day
        )
        today_date = date.today()
        total_days_amount = (today_date - start_date).days + 1

        # Average drinks per day per type
        avg_drinks = (
            DrinkType.objects.all()
            .annotate(avg_per_day=Sum("drink_consumptions__amount") / total_days_amount)
            .order_by("-avg_per_day")
        )
        context["avg_drinks_per_day"] = list(avg_drinks)

        # Data for scatter plot
        scatter_data = (
            DrinkConsumption.objects.select_related("drink_type")
            .values(
                "date",
                "amount",
                "location",
                "drink_type__name",
                "drink_type__image__file",
            )
            .order_by("date")
        )

        # Calculate location coefficient (you may need to adjust this based on your coordinate system)
        for item in scatter_data:
            if item["location"]:
                lat, lon = map(float, item["location"].split(","))
                item["location_coeff"] = (
                    lat + lon
                )  # Simple coefficient, adjust as needed
            else:
                item["location_coeff"] = 0

        context["scatter_data"] = json.dumps(list(scatter_data), cls=CustomJSONEncoder)

        return context
