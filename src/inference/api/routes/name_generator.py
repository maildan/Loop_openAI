"""Name Generator 라우터"""
# pyright: reportImportCycles=false
from __future__ import annotations

from fastapi import APIRouter

from src.inference.api.schemas import (
    NameGenerateRequest,
    MultipleNamesRequest,
    BatchGenerateRequest,
)
from src.utils.name_generator import (
    generate_name,
    generate_multiple_names,
    batch_generate_by_categories,
)

router = APIRouter()

@router.post("/api/generate-name")
async def generate_name_endpoint(request: NameGenerateRequest):
    name = generate_name(
        style=request.style,
        gender=request.gender,
        character_class=request.character_class,
        element=request.element,
    )
    return {"name": name}

@router.post("/api/generate-multiple-names")
async def generate_multiple_names_endpoint(request: MultipleNamesRequest):
    names = generate_multiple_names(
        count=request.count,
        gender=request.gender,
        style=request.style,
    )
    return {"names": names}

@router.post("/api/batch-generate-names")
async def batch_generate_names_endpoint(request: BatchGenerateRequest):
    batch_names = batch_generate_by_categories(count_per_category=request.count_per_category)
    return {"batch_names": batch_names} 