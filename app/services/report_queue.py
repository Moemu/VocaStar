from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import Any, Callable, Coroutine, Optional, cast

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.core.logger import logger
from app.core.sql import async_session
from app.models.career import CareerRecommendation
from app.models.quiz import QuizReport, QuizSubmission
from app.schemas.quiz import QuizReportData, QuizReportPayload
from app.services.holland_report_generator import HollandReportGenerator


@dataclass(slots=True)
class ReportJob:
    report_id: int
    # 回调应返回一个可等待的协程（而非 Task），以便由调用方通过 create_task 调度
    on_complete: Optional[Callable[[int, int], Coroutine[Any, Any, None]]] = None


class ReportTaskQueue:
    """用于异步生成 HollandReport 的简单任务队列。"""

    def __init__(self) -> None:
        self._queue: asyncio.Queue[ReportJob] = asyncio.Queue()
        self._worker: Optional[asyncio.Task[None]] = None
        self._generator = HollandReportGenerator()

    async def start(self) -> None:  # pragma: no cover - 后台生命周期逻辑
        if self._worker is None:
            self._worker = asyncio.create_task(self._run(), name="report-queue-worker")
            logger.info("HollandReport 任务队列已启动")

    async def stop(self) -> None:  # pragma: no cover - 后台生命周期逻辑
        if self._worker is None:
            return
        self._worker.cancel()
        try:
            await self._worker
        except asyncio.CancelledError:  # pragma: no cover - 任务取消兜底（优雅吞掉）
            logger.debug("report-queue-worker 已被取消并正常退出")
        self._worker = None
        logger.info("HollandReport 任务队列已停止")

    async def enqueue(self, job: ReportJob) -> None:
        await self._queue.put(job)
        logger.info("HollandReport 任务入队 report_id=%s", job.report_id)

    async def _run(self) -> None:  # pragma: no cover - 无限循环协程测试价值低
        try:
            while True:
                job = await self._queue.get()
                try:
                    await self._process(job)
                except Exception as exc:  # pragma: no cover - 防止单个任务导致协程退出
                    logger.exception("处理 HollandReport 任务失败 report_id=%s: %s", job.report_id, exc)
                finally:
                    self._queue.task_done()
        except asyncio.CancelledError:  # 在停止时可能发生，优雅退出
            logger.debug("report-queue-worker 收到取消信号，准备退出")
            # 不再抛出，直接结束循环
            return

    async def _process(self, job: ReportJob) -> None:  # pragma: no cover - 依赖 LLM 复杂链路
        async with async_session() as session:
            logger.info("开始处理 HollandReport 任务 report_id=%s", job.report_id)
            stmt = (
                select(QuizReport)
                .where(QuizReport.id == job.report_id)
                .options(
                    selectinload(QuizReport.submission).selectinload(QuizSubmission.user),
                    selectinload(QuizReport.career_recommendations).selectinload(CareerRecommendation.career),
                )
            )
            result = await session.execute(stmt)
            report = result.scalars().first()
            if not report:
                logger.warning("HollandReport 任务找不到报告 report_id=%s", job.report_id)
                return

            report_payload = report.result_json
            report_data = QuizReportData.model_validate(report_payload)
            if report_data.holland_report is not None:
                logger.info("报告已包含 HollandReport，跳过调用 LLM report_id=%s", report.id)
                # 即使报告已存在，也要调用完成回调
                if job.on_complete and report.submission:
                    asyncio.create_task(job.on_complete(report.submission.user_id, job.report_id))
                return

            submission = report.submission
            if not submission:
                logger.warning("报告缺少 submission 关联 report_id=%s", report.id)
                return

            logger.info(
                "准备调用 LLM 生成 HollandReport report_id=%s submission_id=%s user_id=%s",
                report.id,
                submission.id,
                submission.user_id,
            )
            try:
                holland_report = await self._generator.generate(
                    session=session,
                    submission=submission,
                    report_data=report_data,
                )
            except Exception as exc:
                logger.exception(
                    "调用 LLM 生成 HollandReport 失败 report_id=%s submission_id=%s: %s",
                    report.id,
                    submission.id,
                    exc,
                )
                return

            if not holland_report:
                logger.warning(
                    "LLM 返回空结果，HollandReport 未生成 report_id=%s submission_id=%s",
                    report.id,
                    submission.id,
                )
                return

            updated = report_data.model_copy(update={"holland_report": holland_report})
            report.result_json = cast(QuizReportPayload, updated.model_dump(mode="json"))
            await session.commit()
            logger.info("HollandReport 生成完成 report_id=%s submission_id=%s", report.id, submission.id)

            # 报告生成完成后，调用完成回调发送通知
            if job.on_complete:
                asyncio.create_task(job.on_complete(submission.user_id, job.report_id))


report_task_queue = ReportTaskQueue()
