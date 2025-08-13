from .base import Base
from .document import Document


class DataSet(Base):
    class ParserConfig(Base):
        def __init__(self, rag, res_dict):
            super().__init__(rag, res_dict)

    def __init__(self, rag, res_dict):
        self.id = ""
        self.name = ""
        self.avatar = ""
        self.tenant_id = None
        self.description = ""
        self.language = "English"
        self.embedding_model = ""
        self.permission = "me"
        self.document_count = 0
        self.chunk_count = 0
        self.chunk_method = "naive"
        self.parser_config = None
        self.pagerank = 0
        for k in list(res_dict.keys()):
            if k not in self.__dict__:
                res_dict.pop(k)
        super().__init__(rag, res_dict)

    def update(self, user_id: str, update_message: dict):
        """
        Update dataset properties
        """
        # Add user_id to the update message
        update_message["user_id"] = user_id
        res = self.put(f"/datasets/{self.id}", update_message)
        res = res.json()
        if res.get("code") != 0:
            raise Exception(res["message"])

    def upload_documents(self, user_id: str, documents: list[dict]):
        """
        Upload documents to dataset
        document_list: list of dicts with "displayed_name" and "blob" keys
        """
        url = f"/datasets/{self.id}/documents"

        # Prepare files for multipart/form-data upload
        files = []
        for ele in documents:
            # Ensure we have the required fields
            if "displayed_name" not in ele or "blob" not in ele:
                raise ValueError("Each document must have 'displayed_name' and 'blob' keys")
            files.append(("file", (ele["displayed_name"], ele["blob"])))

        # Prepare form data (not JSON, as the API expects multipart/form-data)
        data = {"user_id": user_id}

        # Use files parameter for multipart upload, data for form fields
        res = self.post(path=url, files=files, data=data)
        res = res.json()
        if res.get("code") == 0:
            doc_list = []
            for doc in res["data"]:
                document = Document(self.rag, doc)
                doc_list.append(document)
            return doc_list
        raise Exception(res.get("message"))

    def list_documents(
        self,
        user_id: str,
        id: str | None = None,
        keywords: str | None = None,
        page: int = 1,
        page_size: int = 30,
        orderby: str = "create_time",
        desc: bool = True,
    ):
        """
        List documents in dataset
        """
        params = {
            "user_id": user_id,
            "keywords": keywords,
            "page": page,
            "page_size": page_size,
            "orderby": orderby,
            "desc": desc,
        }
        if id:
            params["id"] = id

        res = self.get(f"/datasets/{self.id}/documents", params=params)
        res = res.json()
        documents = []
        if res.get("code") == 0:
            for document in res["data"].get("docs"):
                documents.append(Document(self.rag, document))
            return documents
        raise Exception(res["message"])

    def delete_documents(self, user_id: str, ids: list[str] | None = None):
        """
        Delete documents from dataset
        """
        res = self.rm(f"/datasets/{self.id}/documents", {"user_id": user_id, "ids": ids})
        res = res.json()
        if res.get("code") != 0:
            raise Exception(res["message"])

    def async_parse_documents(self, user_id: str, document_ids: list[str]):
        """
        Parse documents to generate chunks
        """
        res = self.post(f"/datasets/{self.id}/chunks", {"user_id": user_id, "document_ids": document_ids})
        res = res.json()
        if res.get("code") != 0:
            raise Exception(res.get("message"))

    def async_cancel_parse_documents(self, user_id: str, document_ids: list[str]):
        """
        Stop parsing documents
        """
        res = self.rm(f"/datasets/{self.id}/chunks", {"user_id": user_id, "document_ids": document_ids})
        res = res.json()
        if res.get("code") != 0:
            raise Exception(res.get("message"))

    def download_document(self, document_id: str):
        """
        Download document file
        """
        res = self.get(f"/datasets/{self.id}/documents/{document_id}")
        if res.status_code == 200:
            return res.content
        raise Exception(f"Failed to download document: {res.status_code}")

    def update_document(self, document_id: str, user_id: str, **kwargs):
        """
        Update document properties
        kwargs can include: name, chunk_method, parser_config
        """
        params = {"user_id": user_id}
        params.update(kwargs)

        res = self.put(f"/datasets/{self.id}/documents/{document_id}", params)
        res = res.json()
        if res.get("code") == 0:
            return res["data"]
        raise Exception(res["message"])
