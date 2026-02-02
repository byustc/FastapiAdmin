from collections.abc import Mapping
from typing import Any

from fastapi import status
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy import inspect as sa_inspect
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.background import BackgroundTask

from app.common.constant import RET


class ResponseSchema(BaseModel):
    """响应模型"""

    code: int = Field(default=RET.OK.code, description="业务状态码")
    msg: str = Field(default=RET.OK.msg, description="响应消息")
    data: Any = Field(default=None, description="响应数据")
    status_code: int = Field(default=status.HTTP_200_OK, description="HTTP状态码")
    success: bool = Field(default=True, description="操作是否成功")


class SuccessResponse(JSONResponse):
    """成功响应类"""

    def __init__(
        self,
        data: Any = None,
        msg: str = RET.OK.msg,
        code: int = RET.OK.code,
        status_code: int = status.HTTP_200_OK,
        success: bool = True,
    ) -> None:
        """
        初始化成功响应类

        参数:
        - data (Any | None): 响应数据。
        - msg (str): 响应消息。
        - code (int): 业务状态码。
        - status_code (int): HTTP 状态码。
        - success (bool): 操作是否成功。

        返回:
        - None
        """
        content = ResponseSchema(
            code=code,
            msg=msg,
            data=data,
            status_code=status_code,
            success=success,
        ).model_dump()
        super().__init__(content=content, status_code=status_code)


class ErrorResponse(JSONResponse):
    """错误响应类"""

    def __init__(
        self,
        data: Any = None,
        msg: str = RET.ERROR.msg,
        code: int = RET.ERROR.code,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        success: bool = False,
    ) -> None:
        """
        初始化错误响应类

        参数:
        - data (Any): 响应数据。
        - msg (str): 响应消息。
        - code (int): 业务状态码。
        - status_code (int): HTTP 状态码。
        - success (bool): 操作是否成功。

        返回:
        - None
        """
        content = ResponseSchema(
            code=code,
            msg=msg,
            data=data,
            status_code=status_code,
            success=success,
        ).model_dump()
        super().__init__(content=content, status_code=status_code)


class StreamResponse(StreamingResponse):
    """流式响应类"""

    def __init__(
        self,
        data: Any = None,
        status_code: int = status.HTTP_200_OK,
        headers: Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
    ) -> None:
        """
        初始化流式响应类

        参数:
        - data (Any): 响应数据。
        - status_code (int): HTTP 状态码。
        - headers (Mapping[str, str] | None): 响应头。
        - media_type (str | None): 媒体类型。
        - background (BackgroundTask | None): 后台任务。

        返回:
        - None
        """
        super().__init__(
            content=data,
            status_code=status_code,
            media_type=media_type,  # 文件类型
            headers=headers,  # 文件名
            background=background,  # 文件大小
        )


class UploadFileResponse(FileResponse):
    """
    文件响应
    """

    def __init__(
        self,
        file_path: str,
        filename: str,
        media_type: str = "application/octet-stream",
        headers: Mapping[str, str] | None = None,
        background: BackgroundTask | None = None,
        status_code: int = 200,
    ) -> None:
        """
        初始化文件响应类

        参数:
        - file_path (str): 文件路径。
        - filename (str): 文件名。
        - media_type (str): 文件类型。
        - headers (Mapping[str, str] | None): 响应头。
        - background (BackgroundTask | None): 后台任务。
        - status_code (int): HTTP 状态码。

        返回:
        - None
        """
        super().__init__(
            path=file_path,
            status_code=status_code,
            headers=headers,
            media_type=media_type,
            background=background,
            filename=filename,
            stat_result=None,
            method=None,
            content_disposition_type="attachment",
        )


async def paginate_response(
    db: AsyncSession,
    sql: select,
    page: int,
    size: int,
) -> dict:
    """
    分页响应函数

    参数:
    - db (AsyncSession): 数据库会话
    - sql (select): SQLAlchemy 查询语句
    - page (int): 页码（从1开始）
    - size (int): 每页数量

    返回:
    - dict: 分页数据
        - page_no: 当前页码
        - page_size: 每页数量
        - total: 总记录数
        - has_next: 是否有下一页
        - items: 数据列表
    """
    # 获取总数
    # 尝试从查询中提取模型以优化count查询
    count_sql = select(func.count()).select_from(sql)
    total_result = await db.execute(count_sql)
    total = total_result.scalar() or 0

    # 计算偏移量
    offset = (page - 1) * size

    # 执行分页查询
    result: Result = await db.execute(sql.offset(offset).limit(size))
    items = result.scalars().all()

    return {
        "page_no": page,
        "page_size": size,
        "total": total,
        "has_next": offset + size < total,
        "items": items,
    }
