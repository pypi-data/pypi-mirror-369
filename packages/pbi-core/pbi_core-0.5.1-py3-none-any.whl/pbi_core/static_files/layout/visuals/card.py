from pydantic import ConfigDict

from pbi_core.static_files.layout._base_node import LayoutNode
from pbi_core.static_files.layout.selector import Selector

from .base import BaseVisual
from .column_property import ColumnProperty
from .properties.base import Expression


class CategoryLabelsPropertiesHelper(LayoutNode):
    color: Expression | None = None
    fontFamily: Expression | None = None
    fontSize: Expression | None = None
    show: Expression | None = None


class CategoryLabelsProperties(LayoutNode):
    properties: CategoryLabelsPropertiesHelper
    selector: Selector | None = None


class LabelsPropertiesHelper(LayoutNode):
    color: Expression | None = None
    fontFamily: Expression | None = None
    fontSize: Expression | None = None
    labelPrecision: Expression | None = None
    labelDisplayUnits: Expression | None = None
    preserveWhitespace: Expression | None = None


class LabelsProperties(LayoutNode):
    properties: LabelsPropertiesHelper
    selector: Selector | None = None


class GeneralPropertiesHelper(LayoutNode):
    pass


class GeneralProperties(LayoutNode):
    properties: GeneralPropertiesHelper


class WordWrapperPropertiesHelper(LayoutNode):
    show: Expression | None = None


class WordWrapProperties(LayoutNode):
    properties: WordWrapperPropertiesHelper


class CardProperties(LayoutNode):
    categoryLabels: list[CategoryLabelsProperties] | None = None
    general: list[GeneralProperties] | None = None
    labels: list[LabelsProperties] | None = None
    wordWrap: list[WordWrapProperties] | None = None


class Card(BaseVisual):
    visualType: str = "card"
    model_config = ConfigDict(extra="forbid")

    columnProperties: dict[str, ColumnProperty] | None = None
    drillFilterOtherVisuals: bool = True
    objects: CardProperties | None = None
