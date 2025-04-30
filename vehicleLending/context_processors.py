# vehicleLending/context_processors.py

from .models import BorrowRequest

def borrow_request_notifications(request):
    # only care about logged-in patrons
    if not request.user.is_authenticated:
        return {}

    count = BorrowRequest.objects.filter(
        requester=request.user,
        status__in=['accepted','denied']
    ).count()

    return {'borrow_notification_count': count}
