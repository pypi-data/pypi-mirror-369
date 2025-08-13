from lark_helper.v1.file import download_export_file, get_export_task_result
from tests.config import cloud_platform_token_manager


def test_download_export_file():
    # https://hailiang.feishu.cn/docx/ZkYvdqYjcogmZVxu06CcKWiTnsf
    file_token = "ZkYvdqYjcogmZVxu06CcKWiTnsf"
    # file_type = "docx"
    # export_type = "docx"
    # ticket = create_export_task(cloud_platform_token_manager, file_token, file_type, export_type)
    # print(ticket)
    ticket = "7537206222494547971"
    export_task_result = get_export_task_result(cloud_platform_token_manager, ticket, file_token)
    print(export_task_result)
    file_data = download_export_file(cloud_platform_token_manager, export_task_result.file_token)
    with open("export_file.docx", "wb") as f:
        f.write(file_data)


if __name__ == "__main__":
    test_download_export_file()
