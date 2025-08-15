"""View models for SFMC email templates (HTML, text, subject line, preheader)."""

from typing import Any

from pydantic import BaseModel, Field

from ..base import SFMC_MODEL_CONFIG
from .blocks import Slot


class TemplateReference(BaseModel):
    """Reference to a template asset."""

    model_config = SFMC_MODEL_CONFIG

    id: int = Field(..., description="Template asset ID")
    asset_type: dict[str, int] = Field(
        ..., alias="assetType", description="Template asset type"
    )
    content: str | None = None
    slots: dict[str, Any] | None = None


class HtmlView(BaseModel):
    """HTML view for email templates."""

    model_config = SFMC_MODEL_CONFIG

    content: str = Field(default="", description="HTML content")
    template: TemplateReference | None = None
    slots: dict[str, Slot] = Field(
        default_factory=dict, description="Slots in the HTML view"
    )
    thumbnail: dict[str, Any] = Field(default_factory=dict)
    available_views: list[str] = Field(default_factory=list, alias="availableViews")
    model_version: int = Field(default=2, alias="modelVersion")


class TextView(BaseModel):
    """Text view for email templates."""

    model_config = SFMC_MODEL_CONFIG

    content: str | None = Field(default="", description="Text content")
    generate_from: str | None = Field(default="html", alias="generateFrom")
    thumbnail: dict[str, Any] = Field(default_factory=dict)
    available_views: list[str] = Field(default_factory=list, alias="availableViews")
    model_version: int = Field(default=2, alias="modelVersion")


class SubjectLineView(BaseModel):
    """Subject line view for email templates."""

    model_config = SFMC_MODEL_CONFIG

    content: str = Field(default="", description="Subject line content")
    thumbnail: dict[str, Any] = Field(default_factory=dict)
    available_views: list[str] = Field(default_factory=list, alias="availableViews")
    model_version: int = Field(default=2, alias="modelVersion")


class PreheaderView(BaseModel):
    """Preheader view for email templates."""

    model_config = SFMC_MODEL_CONFIG

    content: str = Field(default="", description="Preheader content")
    thumbnail: dict[str, Any] = Field(default_factory=dict)
    available_views: list[str] = Field(default_factory=list, alias="availableViews")
    model_version: int = Field(default=2, alias="modelVersion")


class EmailViews(BaseModel):
    """Complete email views structure."""

    model_config = SFMC_MODEL_CONFIG

    html: HtmlView | None = None
    text: TextView | None = None
    subjectline: SubjectLineView | None = None
    preheader: PreheaderView | None = None


class Channels(BaseModel):
    """Channel configuration for assets."""

    model_config = SFMC_MODEL_CONFIG

    email: bool = Field(default=True)
    web: bool = Field(default=False)
    mobile: bool | None = None
