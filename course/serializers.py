from rest_framework import serializers


class CreateCourseSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255)
    description = serializers.CharField(max_length=255)
    school_id = serializers.IntegerField()
