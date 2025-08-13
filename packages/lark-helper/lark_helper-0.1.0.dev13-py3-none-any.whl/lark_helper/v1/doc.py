import logging
import re
import time

from lark_helper.constants.doc import UrlPathType
from lark_helper.models.doc import DocumentInfo
from lark_helper.token_manager import TenantAccessTokenManager
from lark_helper.v1.file import (
    create_import_task,
    get_import_task_result,
    upload_media_to_cloud_doc,
)

logger = logging.getLogger(__name__)


def parse_doc_url(url: str) -> DocumentInfo | None:
    paths = [url_type.path for url_type in UrlPathType]
    pattern = f"({'|'.join(re.escape(path) for path in paths)})/([a-zA-Z0-9]+)"

    match = re.search(pattern, url)
    if match:
        path = match.group(1)
        token = match.group(2)

        url_type = UrlPathType.from_path(path)
        if url_type:
            return DocumentInfo(url_type.document_type, token)

    return None


def markdown_to_docx(
    token_manager: TenantAccessTokenManager,
    markdown_content: str,
    doc_name: str,
    mount_key: str,
):
    """
    将markdown内容转换为docx文件
    Args:
        token_manager: 租户访问令牌管理器
        markdown_content: markdown内容
        doc_name: 文件名
        mount_key: 挂载点密钥
    """
    file_name = doc_name
    if not file_name.endswith(".md"):
        file_name = file_name + ".md"

    binary_data = markdown_content.encode("utf-8")
    file_token = upload_media_to_cloud_doc(
        token_manager,
        file_data=binary_data,
        file_name=file_name,
        parent_type="ccm_import_open",
        extra='{"obj_type":"docx","file_extension":"md"}',
    )
    ticket = create_import_task(token_manager, file_token, file_name.replace(".md", ""), mount_key)
    import_task_result = get_import_task_result(token_manager, ticket)
    logger.info(f"ticket: {ticket}, import_task_result: {import_task_result}")
    while import_task_result.job_status in (1, 2):
        time.sleep(1)
        import_task_result = get_import_task_result(token_manager, ticket)
        logger.info(f"ticket: {ticket}, import_task_result: {import_task_result}")
    return import_task_result.url
