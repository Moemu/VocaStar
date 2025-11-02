from __future__ import annotations

import re
import uuid
from datetime import datetime
from pathlib import Path
from typing import Optional

import httpx
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import config
from app.models.community import CommunityPost, CommunityPostAttachment
from app.repositories.posts import PostsRepository
from app.schemas.community import Pagination
from app.schemas.community_posts import (
    AttachmentItem,
    CommentItem,
    CreateCommentRequest,
    LikeState,
    PostAuthor,
    PostItem,
    PostListResponse,
    PublishPostRequest,
    PublishPostResponse,
    RepositoryItem,
)

TITLE_RE = re.compile(r"<title[^>]*>(.*?)</title>", re.IGNORECASE | re.DOTALL)


async def _fetch_url_title(url: str, timeout: float = 3.0) -> Optional[str]:
    try:
        async with httpx.AsyncClient(timeout=timeout, follow_redirects=True) as client:
            resp = await client.get(url)
            if resp.status_code >= 200 and resp.status_code < 400:
                m = TITLE_RE.search(resp.text)
                if m:
                    return m.group(1).strip()[:300]
    except Exception:
        return None
    return None


class PostService:
    def __init__(self, session: AsyncSession) -> None:
        self.repo = PostsRepository(session)
        self.ALLOWED_UPLOAD_TYPES = {"image", "document", "video", "pdf", "code"}

    async def list_posts(
        self,
        *,
        sort: str = "latest",
        page: int = 1,
        page_size: int = 20,
        group_id: Optional[int] = None,
        preview_comments: int = 3,
    ) -> PostListResponse:
        posts, total = await self.repo.list_posts(sort=sort, page=page, page_size=page_size, group_id=group_id)
        post_ids = [p.id for p in posts]
        user_ids = [p.user_id for p in posts]
        attach_map = await self.repo.post_attachments(post_ids)
        author_map = await self.repo.post_authors(user_ids)
        comments_map = await self.repo.post_preview_comments(post_ids, limit=preview_comments)

        items: list[PostItem] = []
        for p in posts:
            username, avatar = author_map.get(p.user_id, ("", None))
            author = PostAuthor(user_id=p.user_id, username=username, avatar_url=avatar)
            attachments: list[AttachmentItem] = []
            for a in attach_map.get(p.id, [])[:50]:
                attachments.append(
                    AttachmentItem(  # type: ignore[arg-type]
                        type=a.type, url=a.url, title=a.title, file_size=a.file_size, download_count=a.download_count
                    )
                )
            comments: list[CommentItem] = []
            for c in comments_map.get(p.id, [])[:preview_comments]:
                # fetch commenter info
                cu = author_map.get(c.user_id)
                comments.append(
                    CommentItem(
                        id=c.id,
                        user_id=c.user_id,
                        username=cu[0] if cu else "",
                        avatar_url=cu[1] if cu else None,
                        content=c.content,
                        likes_count=int(c.likes_count or 0),
                        created_at=c.created_at,
                    )
                )
            items.append(
                PostItem(
                    id=p.id,
                    group_id=p.group_id,
                    title=p.title,
                    content=p.content,
                    author=author,
                    attachments=attachments,
                    likes_count=int(p.likes_count or 0),
                    comments=comments,
                    created_at=p.created_at,
                )
            )

        return PostListResponse(items=items, pagination=Pagination(page=page, page_size=page_size, total=total))

    async def publish_post(self, user_id: int, payload: PublishPostRequest) -> PublishPostResponse:
        # 创建帖子并一次性提交，保证跨请求可见
        p = await self.repo.create_post(
            group_id=payload.group_id, user_id=user_id, title=payload.title, content=payload.content
        )
        # 预处理附件：URL 类型尝试抓取标题
        items: list[tuple[str, str, Optional[str], Optional[int]]] = []
        for att in payload.attachments:
            title = att.title
            if att.type == "url" and not title:
                title = await _fetch_url_title(att.url)
            items.append((att.type, att.url, title, att.file_size))
        if items:
            await self.repo.add_attachments(p.id, items)
        # 提交事务
        await self.repo.session.commit()
        return PublishPostResponse(id=p.id)

    async def like_post(self, user_id: int, post_id: int) -> LikeState:
        liked, count = await self.repo.like_post(user_id, post_id)
        return LikeState(liked=liked, likes_count=count)

    async def comment_post(self, user_id: int, post_id: int, payload: CreateCommentRequest) -> CommentItem:
        c = await self.repo.create_comment(user_id, post_id, payload.content)
        # author info
        username = ""
        avatar = None
        # We can reuse author lookup by a tiny query or leave blank
        return CommentItem(
            id=c.id,
            user_id=c.user_id,
            username=username,
            avatar_url=avatar,
            content=c.content,
            likes_count=int(c.likes_count or 0),
            created_at=c.created_at,
        )

    async def like_group(self, user_id: int, group_id: int) -> LikeState:
        liked, count = await self.repo.like_group(user_id, group_id)
        return LikeState(liked=liked, likes_count=count)

    async def unlike_group(self, user_id: int, group_id: int) -> LikeState:
        liked, count = await self.repo.unlike_group(user_id, group_id)
        return LikeState(liked=liked, likes_count=count)

    async def repository_list(
        self,
        *,
        page: int = 1,
        page_size: int = 20,
        type_filter: Optional[str] = None,
        group_id: Optional[int] = None,
    ) -> tuple[list[RepositoryItem], int]:
        # Build directly using a lightweight query here to avoid extra repository overhead
        att = CommunityPostAttachment
        post = CommunityPost
        conds = [att.post_id == post.id]
        if type_filter and type_filter != "all":
            conds.append(att.type == type_filter)
        if group_id:
            conds.append(post.group_id == group_id)

        total_stmt = select(func.count(att.id)).select_from(att).join(post).where(and_(*conds))
        # retrieve
        stmt = (
            select(att, post.created_at)
            .select_from(att)
            .join(post)
            .where(and_(*conds))
            .order_by(att.created_at.desc())
            .limit(page_size)
            .offset((page - 1) * page_size)
        )
        total = int((await self.repo.session.execute(total_stmt)).scalar() or 0)
        res = await self.repo.session.execute(stmt)
        items: list[RepositoryItem] = []
        for a, published_at in res.all():
            if a.type in ("document", "video", "pdf", "code"):
                items.append(
                    RepositoryItem(
                        type=a.type,
                        title=a.title or "",
                        url=a.url,
                        file_size=a.file_size,
                        published_at=published_at,
                        download_count=int(a.download_count or 0),
                    )
                )
        return items, total

    async def save_uploaded_attachment(self, *, filename: str, data: bytes, att_type: str) -> AttachmentItem:
        """保存社区附件上传内容，并返回 AttachmentItem。

        - 仅允许 att_type ∈ {image, document, video, pdf, code}
        - 文件大小限制见 config.max_upload_size
        - 存储到 static/uploads/YYYY/MM/ 目录，文件名使用 UUID 保留原扩展名
        """
        if att_type not in self.ALLOWED_UPLOAD_TYPES:
            raise ValueError("不支持的附件类型")
        if len(data) > config.max_upload_size:
            raise ValueError("文件过大")

        # 目标目录：/static/uploads/yyyy/mm
        now = datetime.utcnow()
        subdir = Path(str(now.year), f"{now.month:02d}")
        out_dir = config.uploads_dir / subdir
        out_dir.mkdir(parents=True, exist_ok=True)

        # 构造安全文件名
        ext = ""
        if "." in filename:
            ext = "." + filename.split(".")[-1].lower()
        safe_name = f"{uuid.uuid4().hex}{ext}"
        out_path = out_dir / safe_name

        # 写入文件
        with open(out_path, "wb") as f:
            f.write(data)

        url = f"{config.uploads_url_prefix}/{subdir.as_posix()}/{safe_name}"
        title = filename
        size = len(data)
        return AttachmentItem(type=att_type, url=url, title=title, file_size=size, download_count=0)
