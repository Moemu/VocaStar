from __future__ import annotations

from typing import Annotated, Optional

from fastapi import (
    APIRouter,
    Depends,
    File,
    Form,
    HTTPException,
    Query,
    UploadFile,
    status,
)
from sqlalchemy.ext.asyncio import AsyncSession

from app.deps.auth import get_current_user, get_current_user_optional
from app.deps.sql import get_db
from app.models.user import User
from app.schemas.community import (
    CategoryListResponse,
    GroupDetailResponse,
    GroupListResponse,
    MemberListResponse,
    MembershipState,
    Pagination,
)
from app.schemas.community_posts import (
    AttachmentItem,
    CommentItem,
    CreateCommentRequest,
    LikeState,
    PostListResponse,
    PublishPostRequest,
    PublishPostResponse,
    RepositoryListResponse,
)
from app.services.community_service import CommunityService
from app.services.post_service import PostService

router = APIRouter()


# ---- Groups ----


@router.get(
    "/categories",
    response_model=CategoryListResponse,
    summary="获取学习小组分类",
    description="返回用于筛选的分类 chips 列表及每类小组数量（可缓存）",
)
async def list_categories(db: Annotated[AsyncSession, Depends(get_db)]):
    svc = CommunityService(db)
    return await svc.list_categories()


@router.get(
    "",
    response_model=GroupListResponse,
    summary="搜索/筛选学习小组（分页）",
    description=("支持关键字搜索、按分类筛选与排序；未登录时 joined 恒为 false。排序可选 latest|popular|recommended。"),
)
async def list_groups(
    db: Annotated[AsyncSession, Depends(get_db)],
    me: Annotated[Optional[User], Depends(get_current_user_optional)],
    q: Optional[str] = Query(None, description="关键字，匹配小组名称与简介"),
    category: Optional[str] = Query(
        None,
        description="分类标识，例如 frontend/product/design；传 all 或不传表示全部",
    ),
    sort: Optional[str] = Query(
        "latest",
        pattern="^(latest|popular|recommended)$",
        description="排序方式：latest(最新)|popular(最热)|recommended(推荐)",
    ),
    page: int = Query(1, ge=1, description="页码，从 1 开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量，最大 100"),
):
    svc = CommunityService(db)
    return await svc.list_groups(
        q=q, category=category, sort=sort, page=page, page_size=page_size, user_id=me.id if me else None
    )


# 将静态路径 "/my" 放在动态路径 "/{group_id}" 之前，避免被参数路由抢先匹配
@router.get(
    "/my",
    response_model=GroupListResponse,
    summary="我加入的小组（分页）",
    description="返回当前登录用户已加入的小组列表",
)
async def my_groups(
    db: Annotated[AsyncSession, Depends(get_db)],
    me: Annotated[User, Depends(get_current_user)],
    page: int = Query(1, ge=1, description="页码，从 1 开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量，最大 100"),
):
    svc = CommunityService(db)
    return await svc.my_groups(me.id, page=page, page_size=page_size)


@router.get(
    "/{group_id:int}",
    response_model=GroupDetailResponse,
    summary="获取小组详情",
    description="返回小组详情信息；未登录时 joined/liked 为 false",
)
async def group_detail(
    group_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    me: Annotated[Optional[User], Depends(get_current_user_optional)],
):
    svc = CommunityService(db)
    detail = await svc.group_detail(group_id, user_id=me.id if me else None)
    if not detail:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="小组不存在")
    return detail


@router.post(
    "/{group_id:int}/join",
    response_model=MembershipState,
    summary="加入小组（幂等）",
    description="用户加入指定小组；若已加入则直接返回成功状态与成员数",
)
async def join_group(
    group_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    me: Annotated[User, Depends(get_current_user)],
):
    svc = CommunityService(db)
    return await svc.join(me.id, group_id)


@router.delete(
    "/{group_id:int}/membership",
    response_model=MembershipState,
    summary="退出小组（幂等）",
    description="用户退出指定小组；若未加入则返回已退出状态与当前成员数",
)
async def leave_group(
    group_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    me: Annotated[User, Depends(get_current_user)],
):
    svc = CommunityService(db)
    return await svc.leave(me.id, group_id)


@router.get(
    "/{group_id:int}/members",
    response_model=MemberListResponse,
    summary="获取小组成员列表（分页）",
    description="返回小组成员，包含用户名、头像与身份。默认组长优先，按加入时间倒序。",
)
async def list_group_members(
    group_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1, description="页码，从 1 开始"),
    page_size: int = Query(20, ge=1, le=100, description="每页数量，最大 100"),
):
    svc = CommunityService(db)
    return await svc.group_members(group_id, page=page, page_size=page_size)


# ---- Likes ----


@router.post(
    "/{group_id:int}/like",
    response_model=LikeState,
    summary="点赞小组（幂等）",
)
async def like_group(
    group_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    me: Annotated[User, Depends(get_current_user)],
):
    svc = PostService(db)
    return await svc.like_group(me.id, group_id)


@router.delete(
    "/{group_id:int}/like",
    response_model=LikeState,
    summary="取消点赞小组（幂等）",
)
async def unlike_group(
    group_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    me: Annotated[User, Depends(get_current_user)],
):
    svc = PostService(db)
    return await svc.unlike_group(me.id, group_id)


# ---- Feed & Posts ----


@router.get(
    "/feed",
    response_model=PostListResponse,
    summary="获取社区动态（分页）",
    description="支持按最新/最热排序，返回发布者信息、附件、点赞数和部分最新评论。",
)
async def list_feed(
    db: Annotated[AsyncSession, Depends(get_db)],
    sort: str = Query("latest", pattern="^(latest|hottest)$", description="排序方式：latest|hottest"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    group_id: str | None = Query(None, description="可选：限定某个小组的动态（可为空，空视为不筛选）"),
):
    svc = PostService(db)
    gid = None
    if group_id is not None and group_id.strip() != "":
        try:
            gid = int(group_id)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="group_id 应为整数或留空")
    return await svc.list_posts(sort=sort, page=page, page_size=page_size, group_id=gid)


@router.post(
    "/posts",
    response_model=PublishPostResponse,
    summary="发布动态",
    description="创建一条新的社区动态，支持附带图片、外部链接和文档类附件。",
)
async def publish_post(
    db: Annotated[AsyncSession, Depends(get_db)],
    me: Annotated[User, Depends(get_current_user)],
    payload: PublishPostRequest,
):
    svc = PostService(db)
    return await svc.publish_post(me.id, payload)


@router.post(
    "/posts/{post_id:int}/like",
    response_model=LikeState,
    summary="给动态点赞（幂等）",
    description="若已点赞则直接返回 liked=true 与当前点赞数。",
)
async def like_post(
    post_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    me: Annotated[User, Depends(get_current_user)],
):
    svc = PostService(db)
    return await svc.like_post(me.id, post_id)


@router.post(
    "/posts/{post_id:int}/comments",
    response_model=CommentItem,
    summary="在动态下发布评论",
    description="创建一条评论并返回评论条目。",
)
async def comment_post(
    post_id: int,
    db: Annotated[AsyncSession, Depends(get_db)],
    me: Annotated[User, Depends(get_current_user)],
    payload: CreateCommentRequest,
):
    svc = PostService(db)
    return await svc.comment_post(me.id, post_id, payload)


@router.get(
    "/repository",
    response_model=RepositoryListResponse,
    summary="资料库列表（分页）",
    description="收录社区动态中的文档/视频/PDF/代码附件，可按类型与小组过滤。",
)
async def repository_list(
    db: Annotated[AsyncSession, Depends(get_db)],
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    type: str | None = Query("all", pattern="^(all|document|video|pdf|code)$", description="筛选类型"),
    group_id: str | None = Query(None, description="可选：限定某个小组的文库（可为空，空视为不筛选）"),
):
    svc = PostService(db)
    gid = None
    if group_id is not None and group_id.strip() != "":
        try:
            gid = int(group_id)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="group_id 应为整数或留空")
    items, total = await svc.repository_list(page=page, page_size=page_size, type_filter=type, group_id=gid)
    return RepositoryListResponse(items=items, pagination=Pagination(page=page, page_size=page_size, total=total))


# ---- Attachments Upload ----


@router.post(
    "/attachments/upload",
    response_model=AttachmentItem,
    summary="上传社区附件",
    description=(
        "以 multipart/form-data 上传文件，返回可直接用于发布动态附件的 URL 与基本信息。\n"
        "支持类型：image|document|video|pdf|code；最大 20MB（可在配置中调整）。"
    ),
)
async def upload_attachment(
    db: Annotated[AsyncSession, Depends(get_db)],
    me: Annotated[User, Depends(get_current_user)],
    type: str = Form(..., pattern="^(image|document|video|pdf|code)$", description="附件类型"),
    file: UploadFile = File(..., description="要上传的文件"),
):
    data = await file.read()
    svc = PostService(db)
    try:
        return await svc.save_uploaded_attachment(filename=file.filename or "file", data=data, att_type=type)
    except ValueError as e:
        msg = str(e)
        if "文件过大" in msg:
            raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail=msg)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=msg)
