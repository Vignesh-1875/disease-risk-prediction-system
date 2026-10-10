import json
import sqlite3
from datetime import datetime
from types import SimpleNamespace

from bson import ObjectId
from pymongo import ASCENDING, DESCENDING, MongoClient

from ..core.config import DATABASE_NAME, MONGO_URI, PROJECT_ROOT

client = None
db = None


def _json_default(value):
    if isinstance(value, datetime):
        return value.isoformat()
    return str(value)


def _restore(record):
    if isinstance(record.get("created_at"), str):
        record["created_at"] = datetime.fromisoformat(record["created_at"])
    for field in ("_id", "user_id"):
        if field in record and not isinstance(record[field], ObjectId):
            record[field] = ObjectId(record[field])
    return record


class _LocalCursor:
    def __init__(self, records):
        self.records = records

    def sort(self, field, direction):
        self.records.sort(
            key=lambda item: item.get(field, ""),
            reverse=direction == DESCENDING,
        )
        return self

    def __iter__(self):
        return iter(self.records)


class _LocalCollection:
    def __init__(self, connection, table):
        self.connection = connection
        self.table = table

    def insert_one(self, document):
        record = dict(document)
        if self.table == "users" and self.find_one({"email": record.get("email")}):
            raise sqlite3.IntegrityError("UNIQUE constraint failed: users.email")
        record.setdefault("_id", ObjectId())
        self.connection.execute(
            f"INSERT INTO {self.table} (id, data) VALUES (?, ?)",
            (str(record["_id"]), json.dumps(record, default=_json_default)),
        )
        self.connection.commit()
        return SimpleNamespace(inserted_id=record["_id"])

    def _matches(self, record, query):
        return all(str(record.get(key)) == str(value) for key, value in query.items())

    def find_one(self, query, projection=None):
        rows = self.connection.execute(f"SELECT data FROM {self.table}").fetchall()
        for row in rows:
            record = _restore(json.loads(row[0]))
            if self._matches(record, query):
                if projection:
                    record = {
                        key: value
                        for key, value in record.items()
                        if projection.get(key, 1) != 0
                    }
                return record
        return None

    def find(self, query):
        rows = self.connection.execute(f"SELECT data FROM {self.table}").fetchall()
        return _LocalCursor(
            [
                _restore(json.loads(row[0]))
                for row in rows
                if self._matches(json.loads(row[0]), query)
            ]
        )

    def update_one(self, query, update):
        record = self.find_one(query)
        if record and "$set" in update:
            record.update(update["$set"])
            self.connection.execute(
                f"UPDATE {self.table} SET data = ? WHERE id = ?",
                (json.dumps(record, default=_json_default), str(record["_id"])),
            )
            self.connection.commit()


class _LocalDatabase:
    def __init__(self, path):
        self.connection = sqlite3.connect(path, check_same_thread=False)
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS users (id TEXT PRIMARY KEY, data TEXT NOT NULL)"
        )
        self.connection.execute(
            "CREATE TABLE IF NOT EXISTS predictions (id TEXT PRIMARY KEY, data TEXT NOT NULL)"
        )
        self.connection.commit()
        self.users = _LocalCollection(self.connection, "users")
        self.predictions = _LocalCollection(self.connection, "predictions")


def init_database():
    global client, db
    if MONGO_URI:
        try:
            client = MongoClient(MONGO_URI, serverSelectionTimeoutMS=3000)
            client.admin.command("ping")
            db = client[DATABASE_NAME]
            db.users.create_index([("email", ASCENDING)], unique=True)
            db.predictions.create_index([("user_id", ASCENDING), ("created_at", DESCENDING)])
            return db
        except Exception:
            client = None
    db = _LocalDatabase(PROJECT_ROOT / "heart_risk_local.db")
    return db


def get_database():
    if db is None:
        raise RuntimeError("Database has not been initialized.")
    return db
