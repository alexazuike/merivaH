from abc import ABC, abstractmethod


class ReportGenAbstract(ABC):
    """Serves as an abstraction for all reports generator"""

    @abstractmethod
    def gen_daily_report(self):
        pass

    @abstractmethod
    def gen_week_date_report(self):
        pass

    @abstractmethod
    def gen_month_date_report(self):
        pass
