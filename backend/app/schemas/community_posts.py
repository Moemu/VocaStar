from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.schemas.community import Pagination

AttachmentKind = str  # use string type for compatibility; enforce values via validation if needed


class AttachmentItem(BaseModel):
    type: AttachmentKind = Field(..., description="附件类型：image|url|document|video|pdf|code")
    url: str = Field(..., description="附件地址或外部链接")
    title: Optional[str] = Field(None, description="附件标题/文件名；URL 时为页面标题（可为空）")
    file_size: Optional[int] = Field(None, description="字节大小；仅文档/视频/PDF/代码可选")
    download_count: Optional[int] = Field(0, description="下载量；文档/视频/PDF/代码类型返回")


class CommentItem(BaseModel):
    id: int = Field(..., description="评论ID")
    user_id: int = Field(..., description="评论者用户ID")
    username: str = Field(..., description="评论者用户名")
    avatar_url: Optional[str] = Field(None, description="评论者头像")
    content: str = Field(..., description="评论内容")
    likes_count: int = Field(0, description="评论点赞数")
    created_at: datetime = Field(..., description="评论时间")


class PostAuthor(BaseModel):
    user_id: int = Field(..., description="作者ID")
    username: str = Field(..., description="作者用户名/昵称")
    avatar_url: Optional[str] = Field(None, description="作者头像")


class PostItem(BaseModel):
    id: int = Field(..., description="动态ID")
    group_id: int = Field(..., description="所属小组ID")
    title: str = Field(..., description="标题")
    content: str = Field(..., description="正文")
    author: PostAuthor = Field(..., description="发布者信息")
    attachments: list[AttachmentItem] = Field(default_factory=list, description="附件列表")
    likes_count: int = Field(0, description="点赞数")
    comments: list[CommentItem] = Field(default_factory=list, description="预览评论（最多若干条）")
    created_at: datetime = Field(..., description="发布时间")


class PostListResponse(BaseModel):
    items: list[PostItem] = Field(default_factory=list)
    pagination: Pagination


class PublishAttachment(BaseModel):
    """发布动态时的附件项。

    - 当 type 为 url 时，后端会尽力抓取页面标题填充到 title（若未提供）。
    - 当通过上传接口获得文件 URL 时，请将该 URL 作为此处的 url 传入。
    """

    type: AttachmentKind = Field(..., description="附件类型：image|url|document|video|pdf|code")
    url: str = Field(..., description="附件 URL 或外部链接地址（上传成功后返回的 URL 或第三方链接）")
    title: Optional[str] = Field(
        None,
        description="附件标题/文件名；为空时对 url 类型尝试自动解析页面标题",
    )
    file_size: Optional[int] = Field(None, description="文件字节大小；仅文件型附件可选")


class PublishPostRequest(BaseModel):
    group_id: int = Field(..., description="小组ID")
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    attachments: list[PublishAttachment] = Field(default_factory=list)


class PublishPostResponse(BaseModel):
    id: int = Field(..., description="新建动态ID")


class LikeState(BaseModel):
    liked: bool = Field(..., description="当前是否已点赞")
    likes_count: int = Field(..., description="点赞总数")


class CreateCommentRequest(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)


class RepositoryItem(BaseModel):
    type: AttachmentKind = Field(..., description="文库类型：document|video|pdf|code")
    title: str = Field(..., description="文件标题/文件名")
    url: str = Field(..., description="下载/查看地址")
    file_size: Optional[int] = Field(None, description="字节大小")
    published_at: datetime = Field(..., description="发布/收录时间（附件创建时间或动态时间）")
    download_count: int = Field(0, description="下载量")


class RepositoryListResponse(BaseModel):
    items: list[RepositoryItem] = Field(default_factory=list)
    pagination: Pagination
