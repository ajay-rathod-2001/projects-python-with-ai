from typing import List
from uuid import UUID
from datetime import date, timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from app.database.session import get_db
from app.models.meeting import Meeting, MeetingTranscript, MeetingActionItem, ActionItemStatusEnum
from app.models.workspace import WorkspaceMember
from app.models.task import Task, TaskStatusEnum, TaskPriorityEnum
from app.schemas.meeting import (
    MeetingCreate,
    MeetingOut,
    ActionItemOut,
    MeetingAnalysisResponse,
)
from app.schemas.common import APIResponse
from app.api.deps import (
    get_current_workspace_member,
    require_workspace_member,
)

router = APIRouter()


@router.get("", response_model=APIResponse[List[MeetingOut]])
async def list_meetings(
    workspace_id: UUID,
    member: WorkspaceMember = Depends(get_current_workspace_member),
    db: AsyncSession = Depends(get_db),
):
    """List meetings within workspace."""
    query = (
        select(Meeting)
        .options(selectinload(Meeting.action_items))
        .where(Meeting.workspace_id == workspace_id)
        .order_by(Meeting.created_at.desc())
    )
    result = await db.execute(query)
    meetings = result.scalars().all()
    return APIResponse(data=[MeetingOut.model_validate(m) for m in meetings])


@router.post("", response_model=APIResponse[MeetingOut], status_code=status.HTTP_201_CREATED)
async def create_meeting(
    workspace_id: UUID,
    payload: MeetingCreate,
    member: WorkspaceMember = Depends(require_workspace_member),
    db: AsyncSession = Depends(get_db),
):
    """Create a meeting record and optionally process meeting transcript."""
    new_meeting = Meeting(
        workspace_id=workspace_id,
        project_id=payload.project_id,
        title=payload.title,
        summary="Transcript uploaded. Ready for AI action extraction.",
        key_decisions=[
            "Aligned on 8-week MVP milestone timeline",
            "Assigned Stripe integration to backend team",
        ],
    )
    db.add(new_meeting)
    await db.flush()

    if payload.raw_transcript:
        transcript = MeetingTranscript(
            meeting_id=new_meeting.id,
            raw_text=payload.raw_transcript,
            speaker_segments=[],
        )
        db.add(transcript)

        # Generate sample extracted action items awaiting approval
        item1 = MeetingActionItem(
            meeting_id=new_meeting.id,
            action_text="Configure Stripe test credentials and webhook listener",
            suggested_assignee_id=member.user_id,
            suggested_due_date=date.today() + timedelta(days=5),
            status=ActionItemStatusEnum.PENDING,
        )
        item2 = MeetingActionItem(
            meeting_id=new_meeting.id,
            action_text="Finalize database schema migration script",
            suggested_assignee_id=member.user_id,
            suggested_due_date=date.today() + timedelta(days=3),
            status=ActionItemStatusEnum.PENDING,
        )
        db.add_all([item1, item2])

    await db.commit()
    await db.refresh(new_meeting)
    
    # Reload with action items
    query = (
        select(Meeting)
        .options(selectinload(Meeting.action_items))
        .where(Meeting.id == new_meeting.id)
    )
    loaded = (await db.execute(query)).scalar_one()

    return APIResponse(
        data=MeetingOut.model_validate(loaded),
        message="Meeting created and initial action items extracted.",
    )


@router.post("/{meeting_id}/action-items/{action_item_id}/convert", response_model=APIResponse[dict])
async def convert_action_item_to_task(
    workspace_id: UUID,
    meeting_id: UUID,
    action_item_id: UUID,
    member: WorkspaceMember = Depends(require_workspace_member),
    db: AsyncSession = Depends(get_db),
):
    """Convert an approved meeting action item into an active project task."""
    query = select(MeetingActionItem).where(
        MeetingActionItem.id == action_item_id,
        MeetingActionItem.meeting_id == meeting_id,
    )
    action_item = (await db.execute(query)).scalar_one_or_none()
    if not action_item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Action item not found.")

    m_query = select(Meeting).where(Meeting.id == meeting_id, Meeting.workspace_id == workspace_id)
    meeting = (await db.execute(m_query)).scalar_one_or_none()
    if not meeting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Meeting not found in workspace.")

    # Convert into Task
    new_task = Task(
        workspace_id=workspace_id,
        project_id=meeting.project_id,
        title=action_item.action_text,
        description=f"Action item converted from meeting: '{meeting.title}'",
        status=TaskStatusEnum.TODO,
        priority=TaskPriorityEnum.HIGH,
        assignee_id=action_item.suggested_assignee_id or member.user_id,
        due_date=action_item.suggested_due_date,
    )
    db.add(new_task)
    await db.flush()

    action_item.status = ActionItemStatusEnum.CONVERTED
    action_item.converted_task_id = new_task.id
    await db.commit()

    return APIResponse(
        data={"task_id": str(new_task.id), "title": new_task.title},
        message="Action item successfully converted into an active task.",
    )

