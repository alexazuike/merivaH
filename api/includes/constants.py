import os
from django.conf import settings

PRESCRIPTION_BODY_TEMPLATE = os.path.join(
    settings.BASE_DIR, "api", "apps", "pharmacy", "templates", "prescription_body.html"
)

PRESCRIPTION_FOOTER_TEMPLATE = os.path.join(
    settings.BASE_DIR,
    "api",
    "apps",
    "pharmacy",
    "templates",
    "prescription_footer.html",
)
