from enum import Enum
from typing import Optional


class DocumentType(Enum):
    DOCX = "docx"
    SHEET = "sheet"
    MINDNOTE = "mindnote"
    BITABLE = "bitable"
    FILE = "file"
    SLIDES = "slides"
    WIKI = "wiki"
    MINUTES = "minutes"
    FOLDER = "folder"

    @property
    def description(self) -> str:
        descriptions = {
            self.DOCX: "云文档",
            self.SHEET: "表格",
            self.MINDNOTE: "思维导图",
            self.BITABLE: "多维表格",
            self.FILE: "文件",
            self.SLIDES: "幻灯片",
            self.WIKI: "知识库节点",
            self.MINUTES: "妙记文字记录",
            self.FOLDER: "文件夹",
        }
        return descriptions[self]

    @classmethod
    def from_code(cls, code: str) -> Optional["DocumentType"]:
        for doc_type in cls:
            if doc_type.value == code:
                return doc_type
        return None


class UrlPathType(Enum):
    FOLDER = "drive/folder"
    FILE = "file"
    DOCX = "docx"
    SHEETS = "sheets"
    BASE = "base"
    WIKI = "wiki"
    MINUTES = "minutes"

    @property
    def document_type(self) -> DocumentType:
        mapping = {
            self.FOLDER: DocumentType.FOLDER,
            self.FILE: DocumentType.FILE,
            self.DOCX: DocumentType.DOCX,
            self.SHEETS: DocumentType.SHEET,
            self.BASE: DocumentType.BITABLE,
            self.WIKI: DocumentType.WIKI,
            self.MINUTES: DocumentType.MINUTES,
        }
        return mapping[self]

    @property
    def path(self) -> str:
        return self.value

    @classmethod
    def from_path(cls, path: str) -> Optional["UrlPathType"]:
        for url_type in cls:
            if url_type.value == path:
                return url_type
        return None
