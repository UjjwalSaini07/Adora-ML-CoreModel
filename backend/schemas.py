from typing import List, Optional, Dict
from pydantic import BaseModel

class UploadedImage(BaseModel):
    id: str
    role: str  # 'packshot' | 'background' | 'logo' | 'other'
    path: str

class TextBlock(BaseModel):
    id: str
    text: str
    font_size: int
    color: str  # hex
    x: int
    y: int

class CreativeCanvas(BaseModel):
    id: str
    user_id: str
    format: str  # story | feed | banner
    width: int
    height: int
    background_image_id: Optional[str]
    packshot_ids: List[str] = []
    text_blocks: List[TextBlock] = []
    extra: Dict[str, str] = {}

class ValidationIssue(BaseModel):
    code: str
    message: str
    severity: str  # warning | error

class ValidationResult(BaseModel):
    canvas_id: str
    issues: List[ValidationIssue]
    passed: bool

class AutoFixRequest(BaseModel):
    canvas: CreativeCanvas

class AutoFixResponse(BaseModel):
    canvas: CreativeCanvas
    applied_fixes: List[str]
    validation: ValidationResult

class RenderRequest(BaseModel):
    canvas: CreativeCanvas
    formats: List[str]

class RenderedCreative(BaseModel):
    format: str
    path: str
    size_bytes: int

class RenderResponse(BaseModel):
    creatives: List[RenderedCreative]
    audit_log_path: str
