from django.utils import timezone
from rest_framework import serializers

from .models import BlogCategory, BlogPost


class BlogCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = BlogCategory
        fields = ["id", "name", "slug"]


class BlogPostMinimalSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = ["id", "title", "slug", "url"]

    def get_url(self, obj):
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(f"/blog/{obj.slug}/")
        return f"/blog/{obj.slug}/"


class BlogPostListSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    categories = BlogCategorySerializer(source="category", many=True, read_only=True)
    author_name = serializers.CharField(source="author.get_full_name", read_only=True)
    excerpt = serializers.CharField(read_only=True)
    image_url = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = [
            "id",
            "title",
            "slug",
            "url",
            "categories",
            "excerpt",
            "image_url",
            "author_name",
            "published_at",
            "views",
            "language",
            "average_rating",
        ]

    def get_url(self, obj):
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(f"/blog/{obj.slug}/")
        return f"/blog/{obj.slug}/"

    def get_image_url(self, obj):
        if not obj.image:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url

    def get_average_rating(self, obj):
        return obj.average_rating()


class BlogPostDetailSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField()
    categories = BlogCategorySerializer(source="category", many=True, read_only=True)
    author_name = serializers.CharField(source="author.get_full_name", read_only=True)
    author_email = serializers.EmailField(source="author.email", read_only=True)
    image_url = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    total_comments = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = [
            "id",
            "title",
            "slug",
            "url",
            "categories",
            "content",
            "meta_description",
            "meta_keywords",
            "image_url",
            "image_alt",
            "author_name",
            "author_email",
            "created_at",
            "updated_at",
            "is_published",
            "published_at",
            "views",
            "language",
            "average_rating",
            "total_comments",
        ]

    def get_url(self, obj):
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(f"/blog/{obj.slug}/")
        return f"/blog/{obj.slug}/"

    def get_image_url(self, obj):
        if not obj.image:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url

    def get_average_rating(self, obj):
        return obj.average_rating()

    def get_total_comments(self, obj):
        return obj.comments.count()


class BlogPostCreateSerializer(serializers.ModelSerializer):
    category_ids = serializers.PrimaryKeyRelatedField(
        queryset=BlogCategory.objects.all(),
        many=True,
        required=False,
        source="category",
    )
    categories = BlogCategorySerializer(source="category", many=True, read_only=True)
    author_name = serializers.CharField(source="author.get_full_name", read_only=True)
    image_url = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = BlogPost
        fields = [
            "id",
            "title",
            "slug",
            "content",
            "category_ids",
            "categories",
            "image",
            "image_url",
            "image_alt",
            "meta_description",
            "meta_keywords",
            "language",
            "is_published",
            "published_at",
            "author_name",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "author_name", "created_at", "updated_at", "image_url"]

    def validate(self, attrs):
        attrs = super().validate(attrs)
        is_published = attrs.get("is_published", False)
        published_at = attrs.get("published_at")

        if is_published and published_at is None:
            attrs["published_at"] = timezone.now()
        elif not is_published:
            attrs["published_at"] = None

        return attrs

    def create(self, validated_data):
        categories = validated_data.pop("category", [])
        post = BlogPost.objects.create(**validated_data)
        if categories:
            post.category.set(categories)
        return post

    def get_image_url(self, obj):
        if not obj.image:
            return None
        request = self.context.get("request")
        if request:
            return request.build_absolute_uri(obj.image.url)
        return obj.image.url
