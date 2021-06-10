def get_user_data(request):
    """Retrieves User Agent and IP address from headers."""

    forwarded_ip = request.META.get('HTTP_X_FORWARDED_FOR')
    if forwarded_ip:
        ip = forwarded_ip.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')

    data = {
        'user_agent': request.META.get('HTTP_USER_AGENT'),
        'ip': ip,
    }

    return data
