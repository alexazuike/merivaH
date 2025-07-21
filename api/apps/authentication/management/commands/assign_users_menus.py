from django.core.management.base import BaseCommand
from typing import List

from django.contrib.auth.models import User
from api.apps.users.models import UserExtras

menus = [
    {
        "href": "/dashboard/patient",
        "icon": "fas fa-hospital-user",
        "title": "Patient Records",
    },
    {
        "href": "/dashboard/opd",
        "icon": "fas fa-user-md",
        "child": [
            {
                "href": "/dashboard/opd/",
                "icon": "fas fa-list-ul",
                "title": "Encounter Work List",
            }
        ],
        "title": "OPD",
    },
    {
        "href": "/dashboard/laboratory",
        "icon": "fas fa-vial",
        "child": [
            {
                "href": "/dashboard/laboratory/",
                "icon": "fas fa-list-ul",
                "title": "Laboratory Work List",
            }
        ],
        "title": "Laboratory",
    },
    {
        "href": "/dashboard/imaging",
        "icon": "fas fa-x-ray",
        "child": [
            {
                "href": "/dashboard/imaging/",
                "icon": "fas fa-list-ul",
                "title": "Imaging Work List",
            }
        ],
        "title": "Imaging",
    },
    {
        "href": "/dashboard/cso",
        "icon": "fas fa-list-ol",
        "title": "Customer Service Officer",
    },
    {
        "href": "/dashboard/finance",
        "icon": "fas fa-money-check-alt",
        "title": "Finance",
    },
    {
        "href": "/dashboard/reports",
        "icon": "fas fa-file",
        "child": [
            {
                "href": "/dashboard/reports/encounter",
                "icon": "fas fa-list-ul",
                "title": "Encounter report",
            },
            {
                "href": "/dashboard/reports/laboratory",
                "icon": "fas fa-list-ul",
                "title": "Laboratory report",
            },
            {
                "href": "/dashboard/reports/imaging",
                "icon": "fas fa-list-ul",
                "title": "Imaging report",
            },
            {
                "href": "/dashboard/reports/registeration",
                "icon": "fas fa-list-ul",
                "title": "Registeration report",
            },
        ],
        "title": "Reports",
    },
    {
        "href": "/dashboard/configurations",
        "icon": "fas fa-cog",
        "child": [
            {
                "href": "/dashboard/configurations/user/?tab=0",
                "title": "User Management",
            },
            {
                "href": "/dashboard/configurations/finance/",
                "child": [
                    {
                        "href": "/dashboard/configurations/finance/items/",
                        "title": "Billable items",
                    },
                    {
                        "href": "/dashboard/configurations/finance/payment-method/",
                        "title": "Payment methods",
                    },
                ],
                "title": "Finance Configurations",
            },
            {
                "href": "/dashboard/configurations/laboratory/",
                "child": [
                    {
                        "href": "/dashboard/configurations/laboratory/service-center",
                        "title": "Laboratory center",
                    },
                    {
                        "href": "/dashboard/configurations/laboratory/service-config",
                        "title": "Laboratory configuration",
                    },
                ],
                "title": "Laboratory Configurations",
            },
            {
                "href": "/dashboard/configurations/imaging/",
                "child": [
                    {
                        "href": "/dashboard/configurations/imaging/service-center",
                        "title": "Imaging Center",
                    },
                    {
                        "href": "/dashboard/configurations/imaging/service-config",
                        "title": "Imaging Configuration",
                    },
                ],
                "title": "Imaging Configurations",
            },
            {
                "href": "/dashboard/configurations/opd/?tab=0",
                "title": "OPD Configurations",
            },
        ],
        "title": "Configurations",
    },
]


class Command(BaseCommand):
    help = "assign all menus to all users"

    def handle(self, *args, **options):
        users = User.objects.all()
        for user in users:
            user_extras, _ = UserExtras.objects.get_or_create(user=user)
            user_extras.menus = menus
            user_extras.save()
            self.stdout.write(self.style.SUCCESS(f"User {user.username}"))
