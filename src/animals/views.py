import json
from datetime import date
from rest_framework import viewsets
from rest_framework import serializers
from django.utils import timezone
from .models import AnimalSpotting, AnimalType
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


class AnimalSerializer(serializers.ModelSerializer):
    class Meta:
        model = AnimalSpotting
        fields = "__all__"

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data["user"] = user_display_name(instance.spotter)
        return data


class CustomJSONEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, timezone.datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        return super().default(obj)


class AnimalViewSet(viewsets.ModelViewSet):
    queryset = AnimalSpotting.objects.all()
    serializer_class = AnimalSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        user_id = self.request.query_params.get("user")
        if user_id is not None:
            queryset = queryset.filter(spotter_id=user_id)
        return queryset

    @permission_classes([IsAuthenticated, IsAdminUser])
    def perform_create(self, serializer):
        serializer.save(spotter=self.request.user)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["request"] = self.request
        return context

    @action(detail=False, methods=["get"])
    def get_animals_count(self, request):
        animal_type = request.query_params.get("animal_type")

        if animal_type:
            count = AnimalSpotting.objects.filter(animal_type=animal_type).aggregate(
                count=Sum("count")
            )
            return Response({"count": count})

        count = AnimalSpotting.objects.aggregate(count=Sum("count"))
        return Response({"count": count})

    @action(detail=False, methods=["get"])
    def get_total_count_per_type(self, request):
        total_count_per_type = (
            AnimalSpotting.objects.values("animal_type")
            .annotate(total_count=Sum("count"))
            .order_by("animal_type")
        )
        return Response(total_count_per_type)

    @action(detail=False, methods=["post"])
    def quick_add_animal(self, request):
        animal_type_id = request.data.get("animal_type")
        count = request.data.get("count", 1)
        location = request.data.get("location", "")

        if not location:
            stop = ItineraryStop.objects.filter(
                itinerary__stops__start_date__lte=timezone.now(),
                itinerary__stops__end_date__gte=timezone.now(),
                itinerary__stops__location__isnull=False,
            ).first()
            if stop:
                location = stop.location

        AnimalSpotting.objects.create(
            spotter=request.user,
            animal_type_id=animal_type_id,
            count=count,
            location=location,
        )

        return Response({"status": "success"})


class AnimalStatisticsView(TemplateView):
    template_name = "animals-statistics.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        animals_per_user = (
            User.objects.filter(animal_spottings__isnull=False)
            .distinct()
            .annotate(
                total_animals=Sum("animal_spottings__count"),
                total_days=Count("animal_spottings__date", distinct=True),
            )
            .order_by("-total_animals")
        )

        animal_types = AnimalType.objects.all()
        for user in animals_per_user:
            user.animal_breakdown = []
            for animal_type in animal_types:
                count = (
                    AnimalSpotting.objects.filter(
                        spotter=user, animal_type=animal_type
                    ).aggregate(total=Sum("count"))["total"]
                    or 0
                )
                if count > 0:
                    user.animal_breakdown.append(
                        {
                            "name": animal_type.name,
                            "count": count,
                            "image": animal_type.image,
                        }
                    )
            user.animal_breakdown.sort(key=lambda x: x["count"], reverse=True)

        context["animals_per_user"] = animals_per_user

        animals_per_type = (
            AnimalType.objects.filter(animal_spottings__isnull=False)
            .distinct()
            .annotate(
                total_animals=Sum("animal_spottings__count"),
                total_days=Count("animal_spottings__date", distinct=True),
            )
            .order_by("-total_animals")
        )

        users = User.objects.all()
        for animal_type in animals_per_type:
            animal_type.animal_breakdown = []
            for user in users:
                count = (
                    AnimalSpotting.objects.filter(
                        spotter=user, animal_type=animal_type
                    ).aggregate(total=Sum("count"))["total"]
                    or 0
                )
                if count > 0:
                    animal_type.animal_breakdown.append(
                        {
                            "name": user_display_name(user),
                            "count": count,
                            "user": user,
                        }
                    )
            animal_type.animal_breakdown.sort(key=lambda x: x["count"], reverse=True)

        context["animals_per_type"] = animals_per_type

        animals_per_day = (
            AnimalSpotting.objects.annotate(date_day=TruncDate("date"))
            .values("date_day", "animal_type__name")
            .annotate(total=Sum("count"))
            .order_by("date_day")
        )
        context["animals_per_day"] = json.dumps(
            list(animals_per_day), cls=CustomJSONEncoder
        )

        animals_with_location = list(
            AnimalSpotting.objects.exclude(location="").values(
                "location", "count", "animal_type__name", "animal_type__image__file"
            )
        )
        context["animals_with_location"] = json.dumps(
            animals_with_location, cls=CustomJSONEncoder
        )

        start_date = ItineraryStop.objects.order_by("start_date").first().start_date
        today_date = date.today()
        total_days_amount = (today_date - start_date).days + 1

        avg_animals = (
            AnimalType.objects.all()
            .annotate(avg_per_day=Sum("animal_spottings__count") / total_days_amount)
            .order_by("-avg_per_day")
        )
        context["avg_animals_per_day"] = list(avg_animals)

        scatter_data = (
            AnimalSpotting.objects.select_related("animal_type")
            .values(
                "date",
                "count",
                "location",
                "animal_type__name",
                "animal_type__image__file",
            )
            .order_by("date")
        )

        for item in scatter_data:
            if item["location"]:
                lat, lon = map(float, item["location"].split(","))
                item["location_coeff"] = lat + lon
            else:
                item["location_coeff"] = 0

        context["scatter_data"] = json.dumps(list(scatter_data), cls=CustomJSONEncoder)

        return context
