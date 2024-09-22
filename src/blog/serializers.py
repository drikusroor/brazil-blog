from rest_framework import serializers
from .models import Comment, BlogPage
from django.contrib.auth.models import User
from django.urls import reverse
from django_markup.markup import formatter
from blog.templatetags.user_tags import user_display_name, get_user_avatar_url


class UserSerializer(serializers.ModelSerializer):
    avatar = serializers.SerializerMethodField()
    display_name = serializers.SerializerMethodField()
    profile_url = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "avatar",
            "display_name",
            "profile_url",
        ]

    def get_avatar(self, obj):
        return get_user_avatar_url(obj)

    def get_display_name(self, obj):
        return user_display_name(obj)

    def get_profile_url(self, obj):
        return reverse("profile", args=[obj.username])


class RecursiveCommentSerializer(serializers.Serializer):
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        return serializer.data


class CommentSerializer(serializers.ModelSerializer):
    is_author = serializers.SerializerMethodField()
    author_details = UserSerializer(source="author", read_only=True)
    liked_by_user = serializers.SerializerMethodField()
    replies = RecursiveCommentSerializer(many=True, read_only=True)
    rendered_body = serializers.CharField(read_only=True)

    class Meta:
        model = Comment
        fields = [
            "id",
            "post",
            "is_author",
            "author",
            "author_details",
            "body",
            "rendered_body",
            "created_date",
            "updated_date",
            "parent_comment",
            "like_count",
            "liked_by_user",
            "replies",
        ]
        read_only_fields = [
            "id",
            "is_author",
            "author",
            "created_date",
            "updated_date",
            "like_count",
            "liked_by_user",
            "replies",
        ]

    def get_liked_by_user(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return request.user in obj.likes.all()
        return False

    def get_is_author(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return request.user == obj.author
        return False

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["rendered_body"] = formatter(
            instance.body, filter_name="markdown"
        )
        return representation

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
