from django.utils.deprecation import MiddlewareMixin


class ContentSecurityPolicyMiddleware(MiddlewareMixin):
    """Sets a baseline Content Security Policy.

    Adjust as needed when adding external assets.
    """

    def process_response(self, request, response):
        csp = (
            "default-src 'self'; "
            "script-src 'self' https://cdn.jsdelivr.net; "
            "style-src 'self' https://cdn.jsdelivr.net 'unsafe-inline'; "
            "img-src 'self' data:; "
            "font-src 'self' https://cdn.jsdelivr.net; "
            "connect-src 'self' https://api.stripe.com; "
            "frame-src 'self' https://js.stripe.com; "
            "frame-ancestors 'none'"
        )
        response['Content-Security-Policy'] = csp
        return response

