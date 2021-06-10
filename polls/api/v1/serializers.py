from drf_yasg.utils import swagger_serializer_method
from rest_framework import serializers
from rest_framework.exceptions import ValidationError

from polls.models import Poll, Participant, Choice
from polls.utils import get_user_data


class ChoiceIdsSerializer(serializers.Serializer):
    choices_id = serializers.ListField(child=serializers.UUIDField(), allow_empty=False)

    def validate_choices_id(self, choices_id):
        """
        Prepares valid choices for a Poll.
        Returns QuerySet of existing choices in a Poll.
        """

        valid_choices = self.context['poll'].choices.filter(id__in=choices_id)
        return valid_choices

    def validate(self, attrs):
        multi_selection = self.context['poll'].multi_selection
        if attrs['choices_id'].count() > 1 and not multi_selection:
            raise ValidationError({'choices_id': 'multiple choices are not available'})

        return attrs

    def save(self, user_data):
        """
        Saves vote for each choice.
        """

        participant, _ = Participant.objects.get_or_create(
            ip=user_data['ip'], defaults={'user_agent': user_data['user_agent']}
        )

        for choice in self.validated_data['choices_id']:
            choice.participants.add(participant)


class ChoiceSerializer(serializers.ModelSerializer):
    votes = serializers.SerializerMethodField()

    @swagger_serializer_method(serializer_or_field=serializers.IntegerField)
    def get_votes(self, obj):
        """Counts votes for each choice."""
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
        fields = ('id', 'title', 'choices', 'link', 'created_at', 'multi_selection')


class PollCreateSerializer(serializers.ModelSerializer):
    choices = serializers.ListField(allow_empty=False)

    class Meta:
        model = Poll
        fields = ('title', 'choices', 'multi_selection')

    def create(self, validated_data):
        """Performs create the poll."""

        user_data = get_user_data(self.context['request'])
        creator, _ = Participant.objects.get_or_create(
            ip=user_data['ip'], defaults={'user_agent': user_data['user_agent']}
        )
        poll = Poll.objects.create(
            creator=creator,
            title=validated_data['title'],
            multi_selection=validated_data['multi_selection'],
        )

        Choice.objects.bulk_create(
            [Choice(choice=choice, poll=poll) for choice in validated_data['choices']]
        )

        return poll
