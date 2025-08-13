from dataclasses import dataclass

from lark_helper.constants.doc import DocumentType


@dataclass
class DocumentInfo:
    document_type: DocumentType
    node_token: str
