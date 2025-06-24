from django.shortcuts import redirect
from functools import wraps

def premium_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_premium:
            return redirect('upgrade_membership')  # Redirect to upgrade page if not premium
        return view_func(request, *args, **kwargs)
    return _wrapped_view

    