from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

from app.database.session import get_db
from app.core.security import verify_password, get_password_hash, create_access_token, create_refresh_token
from app.core.exceptions import AuthenticationError
from app.models.user import User
from app.models.workspace import Workspace, WorkspaceMember, WorkspaceRoleEnum
from app.schemas.user import UserRegister, UserLogin, UserOut, TokenResponse
from app.schemas.common import APIResponse
from app.api.deps import get_current_user

router = APIRouter()


@router.post("/register", response_model=APIResponse[TokenResponse], status_code=status.HTTP_201_CREATED)
async def register_user(payload: UserRegister, db: AsyncSession = Depends(get_db)):
    """Register a new user manually with email, username, mobile, and password."""
    # Check if email exists
    query = select(User).where(User.email == payload.email.lower())
    existing = (await db.execute(query)).scalar_one_or_none()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists."
        )

    # Check if username exists if provided
    if payload.username:
        u_query = select(User).where(User.username == payload.username.lower())
        existing_u = (await db.execute(u_query)).scalar_one_or_none()
        if existing_u:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This username is already taken. Please choose another."
            )

    # Create User
    new_user = User(
        email=payload.email.lower(),
        username=payload.username.lower() if payload.username else None,
        mobile=payload.mobile if payload.mobile else None,
        hashed_password=get_password_hash(payload.password),
        full_name=payload.full_name,
    )
    db.add(new_user)
    await db.flush()

    # Create default Personal Workspace
    first_name = payload.full_name.split()[0] if payload.full_name else "My"
    workspace_name = f"{first_name}'s Workspace"
    workspace_slug = f"workspace-{str(new_user.id)[:8]}"
    personal_ws = Workspace(
        name=workspace_name,
        slug=workspace_slug,
        owner_id=new_user.id,
    )
    db.add(personal_ws)
    await db.flush()

    # Add as Owner
    membership = WorkspaceMember(
        workspace_id=personal_ws.id,
        user_id=new_user.id,
        role=WorkspaceRoleEnum.OWNER,
    )
    db.add(membership)
    await db.commit()
    await db.refresh(new_user)

    access_token = create_access_token(new_user.id)
    refresh_token = create_refresh_token(new_user.id)

    return APIResponse(
        data=TokenResponse(
            user=UserOut.model_validate(new_user),
            access_token=access_token,
            refresh_token=refresh_token,
        ),
        message="User registered successfully.",
    )


@router.post("/login", response_model=APIResponse[TokenResponse])
async def login_user(payload: UserLogin, db: AsyncSession = Depends(get_db)):
    """Authenticate user with email, username, or mobile and password."""
    ident = payload.identifier.strip().lower()

    # Match against email, username, or mobile
    query = select(User).where(
        or_(
            User.email == ident,
            User.username == ident,
            User.mobile == payload.identifier.strip(),
        )
    )
    user = (await db.execute(query)).scalar_one_or_none()
    
    if not user or not verify_password(payload.password, user.hashed_password):
        raise AuthenticationError("Invalid login credentials. Please check your email/username and password.")

    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User account is deactivated.")

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    return APIResponse(
        data=TokenResponse(
            user=UserOut.model_validate(user),
            access_token=access_token,
            refresh_token=refresh_token,
        ),
        message="Login successful.",
    )


@router.get("/me", response_model=APIResponse[UserOut])
async def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Fetch profile information for authenticated user."""
    return APIResponse(data=UserOut.model_validate(current_user))
