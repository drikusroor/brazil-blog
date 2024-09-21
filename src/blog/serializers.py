from rest_framework import serializers
from .models import Comment, BlogPage
from django.contrib.auth.models import User


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
        ]  # Customize based on the information you want to expose


class CommentSerializer(serializers.ModelSerializer):
    author_details = UserSerializer(source="author", read_only=True)
    liked_by_user = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = [
            "id",
            "post",
            "author",
            "author_details",
            "body",
            "created_date",
            "updated_date",
            "parent_comment",
            "like_count",
            "liked_by_user",
        ]
        read_only_fields = [
            "id",
            "author",
            "created_date",
            "updated_date",
            "like_count",
            "liked_by_user",
        ]

    def get_liked_by_user(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return request.user in obj.likes.all()
        return False

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPage
        fields = ["id", "like_count"]
        read_only_fields = ["like_count"]


class CommentLikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ["id", "like_count"]
        read_only_fields = ["like_count"]
