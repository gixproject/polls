from drf_yasg.utils import swagger_auto_schema
from rest_framework import viewsets, mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response

from polls.api.v1.serializers import PollSerializer, PollCreateSerializer, ChoiceIdsSerializer
from polls.models import Poll
from polls.permissions import IsCreatorIP, CanVote
from polls.utils import get_user_data


class PollViewSet(
    viewsets.GenericViewSet,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer

    def get_serializer_class(self):
        if self.action == 'create':
            return PollCreateSerializer
        return self.serializer_class

    def get_permissions(self):
        if self.action == 'destroy':
            permission_classes = (IsCreatorIP,)
        elif self.action == 'vote':
            permission_classes = (CanVote,)
        else:
            permission_classes = self.permission_classes
        return [permission() for permission in permission_classes]

    @swagger_auto_schema(
        responses={
            status.HTTP_201_CREATED: PollSerializer,
            status.HTTP_400_BAD_REQUEST: 'Bad request',
        })
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        poll = serializer.create(serializer.validated_data)
        data = PollSerializer(poll, context={'request': request}).data

        return Response(status=status.HTTP_201_CREATED, data=data)

    @swagger_auto_schema(
        responses={
            status.HTTP_201_CREATED: PollSerializer,
            status.HTTP_400_BAD_REQUEST: 'Bad request',
            status.HTTP_404_NOT_FOUND: 'Not Found',
        })
    @action(
        detail=True,
        serializer_class=ChoiceIdsSerializer,
        methods=('post',),
    )
    def vote(self, request, pk):
        """
        Multiple choices id are supported.
        """

        poll = self.get_object()
        serializer = ChoiceIdsSerializer(data=request.data, context={'poll': poll})
        serializer.is_valid(raise_exception=True)
        serializer.save(user_data=get_user_data(request=request))

        data = PollSerializer(poll, context={'request': request}).data

        return Response(status=status.HTTP_200_OK, data=data)
