from django.shortcuts import redirect
from functools import wraps

def premium_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.has_premium_access():
            return redirect('upgrade_to_premium')  # Redirect non-premium users
        return view_func(request, *args, **kwargs)
    return _wrapped_view
