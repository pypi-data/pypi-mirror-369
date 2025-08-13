import json

from .base import Base
from .chunk import Chunk


class Document(Base):
    class ParserConfig(Base):
        def __init__(self, rag, res_dict):
            super().__init__(rag, res_dict)

    def __init__(self, rag, res_dict):
        self.id = ""
        self.name = ""
        self.thumbnail = None
        self.dataset_id = None
        self.chunk_method = "naive"
        self.parser_config = {"pages": [[1, 1000000]]}
        self.source_type = "local"
        self.type = ""
        self.created_by = ""
        self.size = 0
        self.token_count = 0
        self.chunk_count = 0
        self.progress = 0.0
        self.progress_msg = ""
        self.process_begin_at = None
        self.process_duration = 0.0
        self.run = "0"
        self.status = "1"
        for k in list(res_dict.keys()):
            if k not in self.__dict__:
                res_dict.pop(k)
        super().__init__(rag, res_dict)

    def update(self, user_id: str, update_message: dict):
        """
        Update document properties
        """
        # Convert update_message to query parameters
        params = {"user_id": user_id}
        params.update(update_message)

        res = self.put(f"/datasets/{self.dataset_id}/documents/{self.id}", params=params)
        res = res.json()
        if res.get("code") != 0:
            raise Exception(res["message"])

    def download(self):
        res = self.get(f"/datasets/{self.dataset_id}/documents/{self.id}")
        try:
            res = res.json()
            raise Exception(res.get("message"))
        except json.JSONDecodeError:
            return res.content

    def list_chunks(self, user_id: str, page=1, page_size=30, keywords=""):
        data = {"user_id": user_id, "keywords": keywords, "offset": page, "limit": page_size}
        res = self.get(f"/datasets/{self.dataset_id}/documents/{self.id}/chunks", data)
        res = res.json()
        if res.get("code") == 0:
            chunks = []
            for data in res["data"].get("chunks"):
                chunk = Chunk(self.rag, data)
                chunks.append(chunk)
            return chunks
        raise Exception(res.get("message"))

    def add_chunk(
        self,
        user_id: str,
        content: str,
        important_keywords: list[str] = [],
        questions: list[str] = [],
        **kwargs,
    ):
        data = {
            "user_id": user_id,
            "content": content,
            "important_keywords": important_keywords,
            "questions": questions,
        }
        data.update(kwargs)
        res = self.post(f"/datasets/{self.dataset_id}/documents/{self.id}/chunks", data)
        res = res.json()
        if res.get("code") == 0:
            return Chunk(self.rag, res["data"].get("chunk"))
        raise Exception(res.get("message"))

    def delete_chunks(self, user_id: str, ids: list[str] | None = None):
        res = self.rm(
            f"/datasets/{self.dataset_id}/documents/{self.id}/chunks",
            {"user_id": user_id, "chunk_ids": ids},
        )
        res = res.json()
        if res.get("code") != 0:
            raise Exception(res.get("message"))

    def update_chunk(
        self,
        chunk_id: str,
        user_id: str,
        content: str = None,
        important_keywords: list[str] = None,
        questions: list[str] = None,
        available: bool = None,
    ):
        """
        Update a specific chunk in the document

        Args:
            chunk_id: The ID of the chunk to update
            user_id: The user ID performing the update
            content: New content for the chunk (optional)
            important_keywords: New important keywords list (optional)
            questions: New questions list (optional)
            available: Whether the chunk is available (optional)
        """
        update_data = {"user_id": user_id}

        if content:
            update_data["content"] = content

        if important_keywords:
            update_data["important_kwd"] = important_keywords

        if questions:
            update_data["question_kwd"] = questions

        if available:
            update_data["available_int"] = 1 if available else 0

        res = self.put(
            f"/datasets/{self.dataset_id}/documents/{self.id}/chunks/{chunk_id}",
            update_data,
        )
        res = res.json()
        if res.get("code") != 0:
            raise Exception(res.get("message"))
