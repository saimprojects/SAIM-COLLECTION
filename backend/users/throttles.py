from rest_framework.throttling import SimpleRateThrottle


class OTPThrottle(SimpleRateThrottle):
    scope = "otp"

    def get_cache_key(self, request, view):
        ident = self.get_ident(request)
        email = request.data.get("email", "")
        return f"throttle_otp_{ident}_{email}"