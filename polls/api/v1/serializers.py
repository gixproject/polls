from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers

from polls.models import Poll, Participant, Choice
from polls.utils import get_ip


class ChoiceIdsSerializer(serializers.Serializer):
    choices_id = serializers.ListField(child=serializers.UUIDField())


class ChoiceSerializer(serializers.ModelSerializer):
    votes = serializers.SerializerMethodField()

    @swagger_serializer_method(serializer_or_field=serializers.IntegerField)
    def get_votes(self, obj):
        return obj.participants.count()

    class Meta:
        model = Choice
        fields = ('choice', 'votes', 'id')


class PollSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True)
    link = serializers.SerializerMethodField(read_only=True)

    def get_link(self, obj):
        return self.context['request'].build_absolute_uri(obj.url)

    class Meta:
        model = Poll
        fields = ('id', 'title', 'choices', 'link', 'created_at')


class PollCreateSerializer(serializers.ModelSerializer):
    choices = serializers.ListField(allow_empty=False)

    class Meta:
        model = Poll
        fields = ('title', 'choices')

    def create(self, validated_data):
        creator_ip = get_ip(self.context['request'])
        creator, _ = Participant.objects.get_or_create(ip=creator_ip)

        poll = Poll.objects.create(creator=creator, title=validated_data['title'])

        Choice.objects.bulk_create(
            [Choice(choice=choice, poll=poll) for choice in validated_data['choices']]
        )

        return poll
