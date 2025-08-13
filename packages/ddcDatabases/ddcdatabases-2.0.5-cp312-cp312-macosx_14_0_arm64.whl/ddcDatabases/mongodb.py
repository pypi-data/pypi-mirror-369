import sys
from contextlib import contextmanager
from datetime import datetime
from ddcDatabases.settings import get_mongodb_settings
from pymongo import ASCENDING, DESCENDING, MongoClient


class MongoDB:
    """
    Class to handle MongoDB connections
    """

    def __init__(
        self,
        host: str | None = None,
        port: int | None = None,
        user: str | None = None,
        password: str | None = None,
        database: str | None = None,
        batch_size: int | None = None,
        limit: int | None = None,
    ):
        _settings = get_mongodb_settings()

        self.host = host or _settings.host
        self.port = port or _settings.port
        self.user = user or _settings.user
        self.password = password or _settings.password
        self.database = database or _settings.database
        self.is_connected = False
        self.client = None
        self.sync_driver = _settings.sync_driver
        self.batch_size = batch_size or _settings.batch_size
        self.limit = limit or _settings.limit

        if not self.user or not self.password:
            raise RuntimeError("Missing username/password")

    def __enter__(self):
        try:
            _connection_url = f"{self.sync_driver}://{self.user}:{self.password}@{self.host}/{self.database}"
            self.client = MongoClient(_connection_url)
            if self._test_connection():
                self.is_connected = True
                return self
        except Exception as e:
            self.client.close() if self.client else None
            sys.exit(1)

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            self.client.close()
            self.is_connected = False

    def _test_connection(self):
        dt = datetime.now().strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
        successful_msg = "[INFO]:Connection to database successful"
        failed_msg = "[ERROR]:Connection to database failed"

        try:
            self.client.admin.command("ping")
            sys.stdout.write(f"[{dt}]:{successful_msg} | {self.user}@{self.host}/{self.database}\n")
            return True
        except Exception as e:
            sys.stderr.write(f"[{dt}]:{failed_msg} | {self.user}@{self.host}/{self.database} | {repr(e)}\n")
            return False

    @contextmanager
    def cursor(self, collection: str, query: dict = None, sort_column: bool = None, sort_direction: str = None):
        col = self.client[self.database][collection]
        if sort_column is not None and sort_direction is not None:
            sort_direction = DESCENDING if sort_direction.lower() in ["descending", "desc"] else ASCENDING
            col.create_index([(sort_column, sort_direction)])
        query = {} if query is None else query
        cursor = col.find(query, batch_size=self.batch_size, limit=self.limit)
        cursor.batch_size(self.batch_size)
        yield cursor
        cursor.close()
