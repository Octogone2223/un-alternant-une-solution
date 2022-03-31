from job.models import JobDating
from rest_framework import serializers


# Serializer for the JobDating model
class JobDatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = JobDating
        fields = "cv", "motivation_letter", "description"


# Serializer for the Job model
class JobCreationSerializer(serializers.Serializer):
    name = serializers.CharField()
    description = serializers.CharField()
    wage = serializers.FloatField()
    contract_type = serializers.CharField()
    start_date = serializers.DateField()
    schedule = serializers.IntegerField()
    company_id = serializers.IntegerField()
