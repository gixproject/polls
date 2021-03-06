from rest_framework.permissions import BasePermission

from polls.utils import get_user_data


class IsCreatorIP(BasePermission):
    """Permission class to check creator IP identity."""

    def has_object_permission(self, request, view, obj):
        request_ip = get_user_data(request=request)['ip']
        return obj.creator.ip == request_ip


class CanVote(BasePermission):
    """
    Permission class to check IP identity of participants.
    Participants mustn't vote for the same poll twice.
    """

    def has_object_permission(self, request, view, obj):
        request_ip = get_user_data(request=request)['ip']
        return not obj.choices.filter(participants__ip=request_ip).exists()
