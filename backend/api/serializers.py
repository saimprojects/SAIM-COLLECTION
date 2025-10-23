from rest_framework import serializers
from .models import ImageAsset


class ElementSerializer(serializers.Serializer):
    id = serializers.CharField()
    type = serializers.ChoiceField(choices=["text"])
    text = serializers.CharField(allow_blank=True)
    x = serializers.IntegerField()
    y = serializers.IntegerField()
    width = serializers.IntegerField()
    height = serializers.IntegerField()
    fontFamily = serializers.CharField()
    fontSize = serializers.IntegerField()
    fill = serializers.CharField()


class ImageAssetSerializer(serializers.ModelSerializer):
    elements = ElementSerializer(many=True)

    class Meta:
        model = ImageAsset
        fields = ["id", "original_image_url", "width", "height", "elements"]