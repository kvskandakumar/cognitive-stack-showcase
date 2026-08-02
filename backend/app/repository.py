import json
import sqlite3
from pathlib import Path
from typing import Any
from uuid import UUID


class PromptRepository:
    def __init__(self, database_path: Path) -> None:
        self.database_path = database_path
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.database_path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        self.database_path.parent.mkdir(parents=True, exist_ok=True)
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS prompts (
                    request_id TEXT PRIMARY KEY,
                    context_id TEXT NOT NULL,
                    prompt TEXT NOT NULL,
                    target_language TEXT NOT NULL,
                    status TEXT NOT NULL,
                    should_call_ai INTEGER NOT NULL,
                    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
                CREATE TABLE IF NOT EXISTS insights (
                    id TEXT PRIMARY KEY,
                    request_id TEXT NOT NULL,
                    position INTEGER NOT NULL,
                    title TEXT NOT NULL,
                    content TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    FOREIGN KEY (request_id) REFERENCES prompts(request_id)
                );
                """
            )

    def save_prompt(
        self,
        *,
        request_id: UUID,
        context_id: UUID,
        prompt: str,
        target_language: str,
        status: str,
        should_call_ai: bool,
        insights: list[dict[str, Any]],
    ) -> None:
        with self._connect() as connection:
            connection.execute(
                """INSERT INTO prompts
                (request_id, context_id, prompt, target_language, status, should_call_ai)
                VALUES (?, ?, ?, ?, ?, ?)""",
                (str(request_id), str(context_id), prompt, target_language, status, should_call_ai),
            )
            connection.executemany(
                """INSERT INTO insights
                (id, request_id, position, title, content, metadata)
                VALUES (?, ?, ?, ?, ?, ?)""",
                [
                    (
                        str(insight["id"]),
                        str(request_id),
                        position,
                        insight["title"],
                        insight["content"],
                        json.dumps(insight["metadata"]),
                    )
                    for position, insight in enumerate(insights)
                ],
            )

    def get_insights(self, request_id: UUID, page: int, page_size: int) -> tuple[list[dict[str, Any]], int] | None:
        offset = (page - 1) * page_size
        with self._connect() as connection:
            exists = connection.execute(
                "SELECT 1 FROM prompts WHERE request_id = ?", (str(request_id),)
            ).fetchone()
            if not exists:
                return None
            total = connection.execute(
                "SELECT COUNT(*) FROM insights WHERE request_id = ?", (str(request_id),)
            ).fetchone()[0]
            rows = connection.execute(
                """SELECT id, title, content, metadata FROM insights
                WHERE request_id = ? ORDER BY position LIMIT ? OFFSET ?""",
                (str(request_id), page_size, offset),
            ).fetchall()
        return (
            [
                {
                    "id": row["id"],
                    "title": row["title"],
                    "content": row["content"],
                    "metadata": json.loads(row["metadata"]),
                }
                for row in rows
            ],
            total,
        )
