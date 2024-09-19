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
        ]
        read_only_fields = ["id", "author", "created_date", "updated_date"]

    def create(self, validated_data):
        validated_data["author"] = self.context["request"].user
        return super().create(validated_data)


class LikeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogPage
        fields = ["id", "like_count"]
        read_only_fields = ["like_count"]
