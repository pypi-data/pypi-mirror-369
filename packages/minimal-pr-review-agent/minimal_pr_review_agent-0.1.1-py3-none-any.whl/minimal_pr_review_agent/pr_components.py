from typing import List, Optional
from enum import Enum
from pydantic import BaseModel, Field


class ReviewCategory(Enum):
    BUG = "bug"
    SYNTAX_ERROR = "syntax_error"
    DOCUMENTATION = "documentation"
    STYLE = "style"
    EDGE_CASE = "edge_case"
    PERFORMANCE = "performance"
    TYPO = "typo"


class FilePatch(BaseModel):
    filename: str
    status: str
    patch: Optional[str] = None
    additions: int
    deletions: int
    changes: int


class ReviewInputs(BaseModel):
    repo: str
    pr_number: int
    title: str
    body: str
    head: str
    base: str
    author: str
    files: List[FilePatch]



class CodeReviewItem(BaseModel):
    file: str
    lines: List[int] = Field(description="[start, end] or [line]")
    category: ReviewCategory
    comment: str
    suggestion: Optional[str] = None


class CodeReviewOutput(BaseModel):
    code_review: List[CodeReviewItem] = Field(default_factory=list)


