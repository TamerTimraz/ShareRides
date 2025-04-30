from .models import BorrowRequest

def borrow_request_notifications(request):
    if not request.user.is_authenticated:
        return {}

    # Pull any newly accepted OR denied requests that we haven’t yet notified the user about
    # (we’ll keep a list of their IDs in the session)
    seen = request.session.get('borrow_notified_ids', [])
    qs = BorrowRequest.objects.filter(
        requester=request.user,
        status__in=['accepted', 'denied']
    ).exclude(id__in=seen)

    count = qs.count()
    if count:
        # record these so we don’t notify again
        request.session['borrow_notified_ids'] = seen + list(qs.values_list('id', flat=True))
        # pass count into the template
        return {'borrow_notification_count': count}
    return {}
