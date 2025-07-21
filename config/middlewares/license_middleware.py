import jwt, socket
from datetime import datetime
from typing import Optional

from dataclasses import dataclass, asdict
from decouple import config
from django.utils import timezone
from django.http import JsonResponse
from dataclasses import dataclass, asdict
from getmac import get_mac_address
from rest_framework import status
from django.http.request import HttpRequest


@dataclass(frozen=True)
class DecryptedLicense:
    expiration_date: str
    exp: Optional[datetime]
    mac_address: Optional[str]
    ip_address: Optional[str]
    users_count: int

    def to_dict(self):
        return asdict(self)


class LicenseMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            decoded_license = self._decode_license()
            self._validate_license(decrypted_data=decoded_license, request=request)
            request.max_users_count = decoded_license.users_count
            response = self.get_response(request)
            return response
        except ValueError as e:
            return JsonResponse(
                data={"status": "Failed", "message": str(e)},
                status=status.HTTP_403_FORBIDDEN,
            )

    def _decode_license(self):
        """
        Decodes License
        """
        license_token = config("license_token", default=None)
        client_public_key = config("client_public_key", default=None)

        if not license_token and not client_public_key:
            raise ValueError("License details not found")
        try:
            license_details = jwt.decode(
                license_token,
                key=client_public_key,
                algorithms=[config("token_algorithm")],
            )
            return DecryptedLicense(**license_details)
        except jwt.PyJWTError:
            raise ValueError("Invalid License")

    def _validate_license(self, decrypted_data: DecryptedLicense, request):
        """Validates License"""
        self._is_expired(expiry_date=decrypted_data.expiration_date)
        self._is_mac_address_valid(mac_address=decrypted_data.mac_address)
        self._is_ip_address_valid(request=request, ip_address=decrypted_data.ip_address)

    def _is_expired(self, expiry_date: str):
        expiry_date = datetime.fromisoformat(expiry_date)
        if timezone.now() > expiry_date:
            raise ValueError("License has expired")

    def _is_mac_address_valid(self, mac_address: str = None):
        if mac_address:
            server_mac_address = get_mac_address()
            if mac_address.strip() != server_mac_address:
                raise ValueError("License is not compatible with server")

    def _is_ip_address_valid(self, request: HttpRequest, ip_address: str = None):
        if ip_address:
            hostname = socket.gethostname()
            server_ip_address = socket.gethostbyname(hostname)
            if server_ip_address.strip() != ip_address.strip():
                raise ValueError("License is not compatible with server")
