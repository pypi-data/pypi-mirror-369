from pydantic import ConfigDict

from pbi_core.static_files.layout._base_node import LayoutNode
from pbi_core.static_files.layout.selector import Selector

from .base import BaseVisual
from .properties.base import Expression


class FillPropertiesHelper(LayoutNode):
    fillColor: Expression | None = None
    image: Expression | None = None
    show: Expression | None = None
    transparency: Expression | None = None


class FillProperties(LayoutNode):
    properties: FillPropertiesHelper
    selector: Selector | None = None


class IconPropertiesHelper(LayoutNode):
    bottomMargin: Expression | None = None
    horizontalAlignment: Expression | None = None
    leftMargin: Expression | None = None
    lineColor: Expression | None = None
    lineTransparency: Expression | None = None
    lineWeight: Expression | None = None
    padding: Expression | None = None
    rightMargin: Expression | None = None
    shapeType: Expression | None = None
    show: Expression | None = None
    topMargin: Expression | None = None
    verticalAlignment: Expression | None = None


class IconProperties(LayoutNode):
    properties: IconPropertiesHelper
    selector: Selector | None = None


class TextPropertiesHelper(LayoutNode):
    fontColor: Expression | None = None
    fontFamily: Expression | None = None
    fontSize: Expression | None = None
    horizontalAlignment: Expression | None = None
    leftMargin: Expression | None = None
    padding: Expression | None = None
    rightMargin: Expression | None = None
    show: Expression | None = None
    text: Expression | None = None
    topMargin: Expression | None = None
    verticalAlignment: Expression | None = None


class TextProperties(LayoutNode):
    properties: TextPropertiesHelper
    selector: Selector | None = None


class OutlinePropertiesHelper(LayoutNode):
    lineColor: Expression | None = None
    roundEdge: Expression | None = None
    show: Expression | None = None
    transparency: Expression | None = None
    weight: Expression | None = None


class OutlineProperties(LayoutNode):
    properties: OutlinePropertiesHelper
    selector: Selector | None = None


class ShapePropertiesHelper(LayoutNode):
    roundEdge: Expression | None = None


class ShapeProperties(LayoutNode):
    properties: ShapePropertiesHelper
    selector: Selector | None = None


class ActionButtonProperties(LayoutNode):
    fill: list[FillProperties] | None = None
    icon: list[IconProperties] | None = None
    outline: list[OutlineProperties] | None = None
    shape: list[ShapeProperties] | None = None
    text: list[TextProperties] | None = None


class ActionButton(BaseVisual):
    visualType: str = "actionButton"
    model_config = ConfigDict(extra="forbid")

    drillFilterOtherVisuals: bool = True
    objects: ActionButtonProperties | None = None
