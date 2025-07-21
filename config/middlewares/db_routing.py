import threading
from enum import Enum

ThreadLocal = threading.local()


class DatabaseTypes(str, Enum):
    SANDBOX = "SANDBOX"
    DEFAULT = "DEfAULT"

    def __str__(self):
        return self.value


class DBRouterMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        DB_TYPE = request.headers.get("db-type") or request.headers.get("Db-Type")
        setattr(ThreadLocal, "DB", self.get_db(DB_TYPE))
        response = self.get_response(request)
        return response

    def get_db(self, db_value: str = None):
        """Gets database name to use

        Args:
            db_value[str]: value gotten from header

        Returns:
            Database Value: either test or production
        """
        if db_value:
            if db_value.casefold() == DatabaseTypes.SANDBOX.casefold():
                return DatabaseTypes.SANDBOX.lower()
        return DatabaseTypes.DEFAULT.lower()


def get_current_db():
    return getattr(ThreadLocal, "DB", DatabaseTypes.DEFAULT.lower())
