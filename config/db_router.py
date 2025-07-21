from .middlewares.db_routing import get_current_db, DatabaseTypes


class AuthRouter:
    """
    A router to control all database operations on models in the
    auth and contenttypes applications.
    """

    route_app_labels = [
        "auth",
        "authentication",
        "users",
        "admin",
        "authtoken",
        "contenttypes",
        "sessions",
    ]

    def db_for_read(self, model, **hints):
        """
        Attempts to read auth and contenttypes models go to auth_db.
        """
        if model._meta.app_label in self.route_app_labels:
            return DatabaseTypes.DEFAULT.lower()
        return None

    def db_for_write(self, model, **hints):
        """
        Attempts to write auth and contenttypes models go to auth_db.
        """
        if model._meta.app_label in self.route_app_labels:
            return DatabaseTypes.DEFAULT.lower()
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """
        Allow relations if a model in the auth or contenttypes apps is
        involved.
        """
        if (
            obj1._meta.app_label in self.route_app_labels
            or obj2._meta.app_label in self.route_app_labels
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Make sure the auth and contenttypes apps only appear in the
        'auth_db' database.
        """
        if app_label in self.route_app_labels:
            return db == DatabaseTypes.DEFAULT.lower()
        return None


class DBRouter:
    """
    Router routes between sandbox and production database
    depending on what was set in the header
    """

    def db_for_read(self, *model, **hints):
        return get_current_db()

    def db_for_write(self, *model, **hints):
        return get_current_db()

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_syncdb(self, *args, **kwargs):
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return True
