import logging
from typing import Callable, List, AnyStr

from apscheduler.triggers.cron import CronTrigger
from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import register_events, register_job

from django.conf import settings

# Create scheduler to run in a thread inside the application process


class SchedulerUtil:
    def __init__(self):
        self.scheduler = BackgroundScheduler(settings.SCHEDULER_CONFIG)

    def add_cron_job(
        self, id: AnyStr, func: Callable[[], None], hour: int = None, minute: int = None
    ):
        """Add job to scheduler

        Args:
            id [str]: job id
            func [Callable]: callback function to add to scheduler

        Return:
            None
        """
        self.scheduler.add_job(
            id=id,
            func=func,
            trigger=CronTrigger(hour=hour, minute=minute),
            replace_existing=True,
        )
        return None

    def start(self):
        """Starts Scheduler"""
        register_events(self.scheduler)
        self.scheduler.start()
        return None
