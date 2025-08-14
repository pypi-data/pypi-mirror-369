import cupy as cp
from pydantic import BaseModel, ConfigDict, Field


class VisageneFace(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    bbox: cp.ndarray = Field(..., description="Bounding box in the format (x1, y1, x2, y2)")
    score: float = Field(..., description="Detection score")
    kps: cp.ndarray = Field(..., description="Keypoints in the format (x, y)")
    matrix: cp.ndarray = Field(..., description="Affine transformation matrix")
    image: cp.ndarray = Field(..., description="Face image")
