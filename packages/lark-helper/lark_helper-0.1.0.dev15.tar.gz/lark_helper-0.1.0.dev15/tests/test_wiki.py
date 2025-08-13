import lark_oapi

from lark_helper.token_manager import TenantAccessTokenManager
from lark_helper.v1.doc import parse_doc_url
from lark_helper.v1.wiki import (
    get_node_space,
    list_space_node,
)

APP_ID = "cli_a4cd2759647ad00c"
APP_SECRET = "P7FoSIEJG7UDUmlHBhiTFfqQan3BbGzU"


# obs:
#     pc:
#       accesskeyid: TKLFY7NLEE40WYYKUZ2U
#       accesskeysecret: qzDPdLzPHmSsKyjA4qH9boynwJANXpQFTSZaoam8
#     endpoint: obs.cn-north-4.myhuaweicloud.com
#     bucket: hljy-resource-collection


# def test_get_node():
#     # https://hailiang.feishu.cn/wiki/PdG3wWa6JiUMxAkCCqucfrV5nHe?table=tblMF6PUGW7dVfHQ&view=vewJjoob5K
#     # https://hailiang.feishu.cn/wiki/PVFMwmXs2iUUcZkyFFYcDVpYnMc?fromScene=spaceOverview
#     token_manager = TenantAccessTokenManager(APP_ID, APP_SECRET)
#     node = get_node_space(token_manager, "wiki", "PVFMwmXs2iUUcZkyFFYcDVpYnMc")
#     print(node)


# def test_get_document():
#     # https://hailiang.feishu.cn/docx/V1yqdT2Hyo9F3kxYqEDcxSQRnZy
#     token_manager = TenantAccessTokenManager(APP_ID, APP_SECRET)
#     document = get_file_meta(token_manager, "PeuMbsRN9oGibVxnEiCcqZuhnLe", "file")
#     print(document)


def test_get_child_node():
    token_manager = TenantAccessTokenManager(APP_ID, APP_SECRET)
    node = get_node_space(token_manager, "wiki", "PVFMwmXs2iUUcZkyFFYcDVpYnMc")
    if node.has_child:
        node_list = list_space_node(token_manager, node.space_id, node.node_token)
        print(node_list)
        lark_oapi.logger.info(lark_oapi.JSON.marshal(node_list, indent=4))
        for node in node_list:
            if node.has_child:
                node_list = list_space_node(token_manager, node.space_id, node.node_token)
                print(node_list)
                lark_oapi.logger.info(lark_oapi.JSON.marshal(node_list, indent=4))


def test():
    test_urls = [
        "https://hailiang.feishu.cn/wiki/WDs9wdrpciIRexkzkthc7q9inLh?table=tblpZUZhrRxMFBbu&view=vewhjExHby",
        "https://hailiang.feishu.cn/minutes/obcncdikf7za676ip1o8n43u?from=from_parent_sheet",
        "https://hailiang.feishu.cn/wiki/A2PgwyuAHilz3CkIkdHcAaRZnie",
        "https://hailiang.feishu.cn/docx/NGMAduXLro9l5IxlLLEc98kJnmf",
        "https://hailiang.feishu.cn/file/W73hbTj5Vos8Anxgig4cgiIQnge",
        "https://hailiang.feishu.cn/drive/folder/MeKPfEFFXl5WYkdWkISci41NnCc?from=space_shared_folder&fromShareWithMeNew=1",
    ]

    for url in test_urls:
        print(parse_doc_url(url))
