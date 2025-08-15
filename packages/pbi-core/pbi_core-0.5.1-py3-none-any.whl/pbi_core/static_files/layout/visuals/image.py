from pydantic import ConfigDict

from pbi_core.static_files.layout._base_node import LayoutNode

from .base import BaseVisual
from .column_property import ColumnProperty
from .properties.base import Expression


class GeneralPropertiesHelper(LayoutNode):
    imageUrl: Expression | None = None


class GeneralProperties(LayoutNode):
    properties: GeneralPropertiesHelper


class ImageScalingPropertiesHelper(LayoutNode):
    imageScalingType: Expression | None = None


class ImageScalingProperties(LayoutNode):
    properties: ImageScalingPropertiesHelper


class ImageProperties(LayoutNode):
    general: list[GeneralProperties] | None = None
    imageScaling: list[ImageScalingProperties] | None = None


class Image(BaseVisual):
    visualType: str = "image"
    model_config = ConfigDict(extra="forbid")

    columnProperties: dict[str, ColumnProperty] | None = None
    drillFilterOtherVisuals: bool = True
    objects: ImageProperties | None = None
