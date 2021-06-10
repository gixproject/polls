from polls.models import Participant, Choice


def get_ip(request):
    """Retrieves IP address from headers."""

    forwarded_ip = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_ip:
        ip = forwarded_ip.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    return ip


def perform_vote(choices_id, participant_ip):
    """Vote for choice."""

    participant, _ = Participant.objects.get_or_create(ip=participant_ip)

    for choice_id in choices_id:
        choice = Choice.objects.get(id=choice_id)
        choice.participants.add(participant)
