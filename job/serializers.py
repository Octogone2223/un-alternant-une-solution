from job.models import JobDating
from rest_framework import serializers


class JobDatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobDating
        fields = 'cv', 'motivation_letter', 'description'
