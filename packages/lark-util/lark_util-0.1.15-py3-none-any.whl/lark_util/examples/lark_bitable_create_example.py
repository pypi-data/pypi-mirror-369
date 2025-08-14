"""飞书多维表格新增记录示例"""

import os
import lark_oapi as lark

from lark_util.examples.mock_record import (
    APP_TOKEN,
    TABLE_ID,
    generate_mock_app_table_record,
    generate_mock_fields,
)
from ..lark_bitable import create_bitable_record


def main():
    # 字段值
    mock_fields = generate_mock_fields()
    # 新增记录
    try:
        result = create_bitable_record(APP_TOKEN, TABLE_ID, mock_fields)
        print(f"新增记录成功: {lark.JSON.marshal(result, indent=2)}")
    except Exception as e:
        print(f"新增记录失败: {e}")


if __name__ == "__main__":
    main()
