from __future__ import annotations

import json
import uuid
from copy import deepcopy
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config import settings


class LocalCollection:
    def __init__(self, path: Path, name: str):
        self.path = path
        self.name = name
        self.path.mkdir(parents=True, exist_ok=True)
        self.file = self.path / f"{name}.json"
        if not self.file.exists():
            self.file.write_text("[]", encoding="utf-8")

    def _read(self) -> list[dict[str, Any]]:
        return json.loads(self.file.read_text(encoding="utf-8") or "[]")

    def _write(self, docs: list[dict[str, Any]]) -> None:
        self.file.write_text(json.dumps(docs, indent=2, default=str), encoding="utf-8")

    def find(self, query: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        query = query or {}
        return [deepcopy(doc) for doc in self._read() if _matches(doc, query)]

    def find_one(self, query: dict[str, Any]) -> dict[str, Any] | None:
        for doc in self.find(query):
            return doc
        return None

    def insert_one(self, document: dict[str, Any]):
        docs = self._read()
        doc = deepcopy(document)
        doc.setdefault("_id", str(uuid.uuid4()))
        doc.setdefault("created_at", utc_now())
        doc["updated_at"] = utc_now()
        docs.append(doc)
        self._write(docs)
        return type("InsertOneResult", (), {"inserted_id": doc["_id"]})

    def update_one(self, query: dict[str, Any], update: dict[str, Any], upsert: bool = False):
        docs = self._read()
        for index, doc in enumerate(docs):
            if _matches(doc, query):
                _apply_update(doc, update)
                doc["updated_at"] = utc_now()
                docs[index] = doc
                self._write(docs)
                return type("UpdateResult", (), {"matched_count": 1, "modified_count": 1})
        if upsert:
            new_doc = {k: v for k, v in query.items() if not k.startswith("$")}
            _apply_update(new_doc, update)
            self.insert_one(new_doc)
            return type("UpdateResult", (), {"matched_count": 0, "modified_count": 1})
        return type("UpdateResult", (), {"matched_count": 0, "modified_count": 0})

    def delete_many(self, query: dict[str, Any]):
        docs = self._read()
        remaining = [doc for doc in docs if not _matches(doc, query)]
        deleted_count = len(docs) - len(remaining)
        self._write(remaining)
        return type("DeleteResult", (), {"deleted_count": deleted_count})


class MongoGateway:
    def __init__(self):
        self.is_connected = False
        self._client = None
        self._db = None
        self._local_root = settings.project_root / "local_store"
        self._local_collections: dict[str, LocalCollection] = {}
        if settings.mongodb_uri:
            try:
                from pymongo import MongoClient

                self._client = MongoClient(settings.mongodb_uri, serverSelectionTimeoutMS=2500)
                self._client.admin.command("ping")
                self._db = self._client[settings.mongodb_database]
                self.is_connected = True
            except Exception:
                self.is_connected = False

    def collection(self, name: str):
        if self.is_connected and self._db is not None:
            return self._db[name]
        if name not in self._local_collections:
            self._local_collections[name] = LocalCollection(self._local_root, name)
        return self._local_collections[name]

    def find(self, collection: str, query: dict[str, Any] | None = None) -> list[dict[str, Any]]:
        return list(self.collection(collection).find(query or {}))

    def find_one(self, collection: str, query: dict[str, Any]) -> dict[str, Any] | None:
        return self.collection(collection).find_one(query)

    def insert(self, collection: str, document: dict[str, Any]) -> str:
        document.setdefault("_id", str(uuid.uuid4()))
        result = self.collection(collection).insert_one(document)
        return str(result.inserted_id)

    def upsert(self, collection: str, query: dict[str, Any], document: dict[str, Any]) -> None:
        self.collection(collection).update_one(query, {"$set": document}, upsert=True)

    def update(self, collection: str, query: dict[str, Any], update: dict[str, Any]) -> None:
        self.collection(collection).update_one(query, update, upsert=False)

    def delete_many(self, collection: str, query: dict[str, Any]) -> int:
        result = self.collection(collection).delete_many(query)
        return int(getattr(result, "deleted_count", 0))


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _matches(doc: dict[str, Any], query: dict[str, Any]) -> bool:
    for key, expected in query.items():
        value = doc.get(key)
        if isinstance(expected, dict) and "$in" in expected:
            if value not in expected["$in"]:
                return False
        elif str(value) != str(expected):
            return False
    return True


def _apply_update(doc: dict[str, Any], update: dict[str, Any]) -> None:
    if "$set" in update:
        for key, value in update["$set"].items():
            doc[key] = value
    if "$push" in update:
        for key, value in update["$push"].items():
            doc.setdefault(key, []).append(value)


mongo = MongoGateway()
