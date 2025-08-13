import lark_oapi as lark
from lark_oapi.api.docx.v1 import GetDocumentRequest, GetDocumentResponse
from lark_oapi.api.drive.v1 import (
    BatchQueryMetaRequest,
    BatchQueryMetaResponse,
    MetaRequest,
    RequestDoc,
)
from lark_oapi.api.wiki.v2 import (
    GetNodeSpaceRequest,
    GetNodeSpaceResponse,
    ListSpaceNodeRequest,
    ListSpaceNodeRequestBuilder,
    ListSpaceNodeResponse,
    Node,
)

from lark_helper.exception import LarkResponseError
from lark_helper.token_manager import TenantAccessTokenManager


def get_node_space(
    token_manager: TenantAccessTokenManager, doc_type: str, token: str
) -> Node | None:
    """
    获取知识空间节点信息
    https://open.feishu.cn/document/server-docs/docs/wiki-v2/space-node/get_node
    """
    client = token_manager.get_lark_client()

    request: GetNodeSpaceRequest = (
        GetNodeSpaceRequest.builder().token(token).obj_type(doc_type).build()
    )

    response: GetNodeSpaceResponse = client.wiki.v2.space.get_node(request)

    # 处理失败返回
    if not response.success():
        error_msg = f"client.wiki.v2.space.get_node failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}"
        lark.logger.error(error_msg)
        raise LarkResponseError(error_msg)

    # 处理业务结果
    lark.logger.info(lark.JSON.marshal(response.data, indent=4))
    return response.data.node


def list_space_node(
    token_manager: TenantAccessTokenManager,
    space_id: str,
    parent_node_token: str,
    page_size: int = 50,
    page_token: str | None = None,
):
    """
    获取知识空间子节点列表
    https://open.feishu.cn/document/server-docs/docs/wiki-v2/space-node/list
    """
    client = token_manager.get_lark_client()

    # 构造请求对象
    request_builder: ListSpaceNodeRequestBuilder = (
        ListSpaceNodeRequest.builder()
        .space_id(space_id)
        .page_size(page_size)
        .parent_node_token(parent_node_token)
    )
    if page_token:
        request_builder.page_token(page_token)
    request: ListSpaceNodeRequest = request_builder.build()

    # 发起请求
    response: ListSpaceNodeResponse = client.wiki.v2.space_node.list(request)

    # 处理失败返回
    if not response.success():
        error_msg = f"client.wiki.v2.space_node.list failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}"
        lark.logger.error(error_msg)
        raise LarkResponseError(error_msg)

    node_list = response.data.items
    # 处理业务结果
    lark.logger.debug(lark.JSON.marshal(response.data, indent=4))
    while response.data.has_more:
        request.page_token = response.data.page_token
        response: ListSpaceNodeResponse = client.wiki.v2.space_node.list(request)
        node_list.extend(response.data.items)
        lark.logger.debug(lark.JSON.marshal(response.data, indent=4))

    return node_list


def get_document(token_manager: TenantAccessTokenManager, document_id: str) -> dict:
    """
    获取文档基本信息
    https://open.feishu.cn/document/server-docs/docs/docs/docx-v1/document/get
    """
    client = token_manager.get_lark_client()

    request: GetDocumentRequest = GetDocumentRequest.builder().document_id(document_id).build()

    response: GetDocumentResponse = client.docx.v1.document.get(request)

    # 处理失败返回
    if not response.success():
        error_msg = f"client.docx.v1.document.get failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}"
        lark.logger.error(error_msg)
        raise LarkResponseError(error_msg)

    # 处理业务结果
    lark.logger.info(lark.JSON.marshal(response.data, indent=4))

    return response.data


def get_file_meta(token_manager: TenantAccessTokenManager, doc_token: str, doc_type: str) -> dict:
    """
    获取文件元数据
    https://open.feishu.cn/document/server-docs/docs/drive-v1/file/batch_query
    """
    client = token_manager.get_lark_client()

    request: BatchQueryMetaRequest = (
        BatchQueryMetaRequest.builder()
        .user_id_type("open_id")
        .request_body(
            MetaRequest.builder()
            .request_docs([RequestDoc.builder().doc_token(doc_token).doc_type(doc_type).build()])
            .with_url(False)
            .build()
        )
        .build()
    )

    # 发起请求
    response: BatchQueryMetaResponse = client.drive.v1.meta.batch_query(request)

    # 处理失败返回
    if not response.success():
        error_msg = f"client.drive.v1.meta.batch_query failed, code: {response.code}, msg: {response.msg}, log_id: {response.get_log_id()}"
        lark.logger.error(error_msg)
        raise LarkResponseError(error_msg)

    # 处理业务结果
    lark.logger.info(lark.JSON.marshal(response.data, indent=4))
    return response.data
