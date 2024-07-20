from django.shortcuts import redirect
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin

class ApprovalCheckMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.user.is_authenticated and hasattr(request.user, 'member'):
            if not request.user.member.is_approved:
                messages.warning(request, 'Your account is not yet approved by an admin.')
                return redirect('home')  # Redirect to the home page or another page
