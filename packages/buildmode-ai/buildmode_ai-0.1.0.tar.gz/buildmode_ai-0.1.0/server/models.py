# models.py

from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    TIMESTAMP,
    JSON,
    ForeignKey,
)
from sqlalchemy.sql import func

# Import the Base class from our new database.py file
from server.database import Base


class MemoryFile(Base):
    __tablename__ = "memory_files"
    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, unique=True, index=True, nullable=False)
    summary = Column(Text)
    functions = Column(JSON)  # Store as JSON for SQLite compatibility
    components = Column(JSON)  # Store as JSON for SQLite compatibility
    api_routes = Column(JSON)  # Store as JSON for SQLite compatibility
    last_inspected_at = Column(
        TIMESTAMP(timezone=True), server_default=func.now()
    )
    file_size = Column(Integer)
    language = Column(String)
    commit_sha = Column(String)
    full_text = Column(Text)
    embedding = Column(JSON)


class MemoryReport(Base):
    __tablename__ = "memory_reports"
    id = Column(Integer, primary_key=True, index=True)
    tool_name = Column(String, nullable=False)
    report = Column(JSON)
    generated_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class EditLog(Base):
    __tablename__ = "edit_logs"
    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, nullable=False)
    editor_info = Column(Text)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now())


class TaskQueue(Base):
    __tablename__ = "task_queue"
    id = Column(String, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    description = Column(Text)
    priority = Column(Integer, default=0)
    phase = Column(String)
    status = Column(String, nullable=False)
    task_type = Column(String, default="general")
    assignee = Column(String)
    parent_id = Column(String, ForeignKey("task_queue.id"))
    epic_id = Column(String, ForeignKey("epics.id"))
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class Goal(Base):
    __tablename__ = "goals"
    id = Column(String, primary_key=True, index=True)
    title = Column(Text, nullable=False)


class Epic(Base):
    __tablename__ = "epics"
    id = Column(String, primary_key=True, index=True)
    title = Column(Text, nullable=False)
    goal_id = Column(String, ForeignKey("goals.id"))


class Channel(Base):
    __tablename__ = "channels"
    id = Column(String, primary_key=True, index=True)
    title = Column(String)
    description = Column(Text)
    custom_url = Column(String)
    published_at = Column(TIMESTAMP(timezone=True))
    thumbnail_url = Column(String)
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class Video(Base):
    __tablename__ = "videos"
    id = Column(String, primary_key=True, index=True)
    channel_id = Column(String, ForeignKey("channels.id"))
    title = Column(String)
    description = Column(Text)
    published_at = Column(TIMESTAMP(timezone=True))
    thumbnail_url = Column(String)


class MemoryEntry(Base):
    """Generic memory storage for arbitrary text snippets."""

    __tablename__ = "memory_entries"
    id = Column(Integer, primary_key=True, index=True)
    file_path = Column(String, unique=True, index=True, nullable=False)
    summary = Column(Text)
    full_text = Column(Text)
    notes = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class TaskPlanModel(Base):
    """Database model for storing task plans."""

    __tablename__ = "task_plans"

    task_id = Column(String, primary_key=True, index=True)
    description = Column(Text, nullable=False)
    status = Column(String, nullable=False)
    related_files = Column(JSON, nullable=False)
    steps = Column(JSON, nullable=False)


class BuildLog(Base):
    """Database model for storing build logs."""

    __tablename__ = "build_logs"

    id = Column(Integer, primary_key=True, index=True)
    build_id = Column(String, index=True, nullable=False)
    log_content = Column(Text, nullable=False)
    metadata_ = Column("metadata", JSON)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class PromptFeedback(Base):
    """Store corrections to prompts."""

    __tablename__ = "prompt_feedback"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, index=True, nullable=False)
    original_prompt = Column(Text, nullable=False)
    correction = Column(Text)
    updated_prompt = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class CommitHistory(Base):
    """Record git commits pushed by the build agent."""

    __tablename__ = "commit_history"

    id = Column(Integer, primary_key=True, index=True)
    commit_sha = Column(String, index=True, nullable=False)
    message = Column(Text)
    diff_text = Column(Text)
    author = Column(String)
    timestamp = Column(TIMESTAMP(timezone=True))
    summary = Column(Text)


class RuntimeLog(Base):
    """Log entries parsed from deployment runtime logs (e.g., Railway)."""

    __tablename__ = "runtime_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(TIMESTAMP(timezone=True), nullable=False)
    service = Column(String, nullable=False)
    level = Column(String, nullable=False)
    message = Column(Text, nullable=False)


class TaskComment(Base):
    """User or system comments attached to tasks."""

    __tablename__ = "task_comments"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(
        String, ForeignKey("task_queue.id"), index=True, nullable=False
    )
    comment = Column(Text, nullable=False)
    author = Column(String, default="system")
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, nullable=False, index=True)
    role = Column(String, default="user")


class Vision(Base):
    __tablename__ = "visions"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True, nullable=False)
    vision = Column(Text, nullable=False)
    anti_vision = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class CorrectionLog(Base):
    """Record attempts to correct agent behavior."""

    __tablename__ = "correction_logs"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(String, index=True, nullable=False)
    agent = Column(String, nullable=False)
    outcome = Column(Text)
    human_feedback = Column(Text)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())


class AgentActionLog(Base):
    """Record notable agent actions."""

    __tablename__ = "agent_action_logs"
    id = Column(Integer, primary_key=True, index=True)
    agent = Column(String, nullable=False)
    action = Column(String, nullable=False)
    sha = Column(String)
    metadata_ = Column("metadata", JSON)
    timestamp = Column(TIMESTAMP(timezone=True), server_default=func.now())
