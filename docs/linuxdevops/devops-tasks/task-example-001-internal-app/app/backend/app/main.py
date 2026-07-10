from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from .auth import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from .database import Base, engine, get_db
from .models import Message, User
from .schemas import (
    LoginRequest,
    MessageCreate,
    MessageOut,
    RegisterRequest,
    TokenResponse,
    UserOut,
)

app = FastAPI(title="Internal Messages", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
    Base.metadata.create_all(bind=engine)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/api/register", response_model=TokenResponse)
def register(body: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    existing = db.query(User).filter(User.username == body.username).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Username already taken"
        )

    user = User(username=body.username, password_hash=hash_password(body.password))
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token(user.id, user.username)
    return TokenResponse(access_token=token, username=user.username)


@app.post("/api/login", response_model=TokenResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.query(User).filter(User.username == body.username).first()
    if user is None or not verify_password(body.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    token = create_access_token(user.id, user.username)
    return TokenResponse(access_token=token, username=user.username)


@app.get("/api/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> User:
    return user


@app.post("/api/messages", response_model=MessageOut, status_code=status.HTTP_201_CREATED)
def create_message(
    body: MessageCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> Message:
    msg = Message(user_id=user.id, text=body.text.strip())
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return msg


@app.get("/api/messages", response_model=list[MessageOut])
def list_messages(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[Message]:
    return (
        db.query(Message)
        .filter(Message.user_id == user.id)
        .order_by(Message.created_at.desc())
        .all()
    )
