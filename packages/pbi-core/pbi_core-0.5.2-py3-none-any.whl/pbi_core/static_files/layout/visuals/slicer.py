from pydantic import ConfigDict, Field

from pbi_core.static_files.layout._base_node import LayoutNode
from pbi_core.static_files.layout.expansion_state import ExpansionState
from pbi_core.static_files.layout.filters import Filter
from pbi_core.static_files.layout.selector import SelectorData

from .base import BaseVisual
from .properties.base import Expression
from .table import ColumnProperty


class SyncGroup(LayoutNode):
    groupName: str
    fieldChanges: bool
    filterChanges: bool = True


class CachedFilterDisplayItems(LayoutNode):
    id: SelectorData
    displayName: str


class HeaderPropertiesHelper(LayoutNode):
    background: Expression | None = None
    fontColor: Expression | None = None
    fontFamily: Expression | None = None
    show: Expression | None = None
    showRestatement: Expression | None = None
    textSize: Expression | None = None


class HeaderProperties(LayoutNode):
    properties: HeaderPropertiesHelper = Field(default_factory=HeaderPropertiesHelper)


class GeneralPropertiesHelper(LayoutNode):
    filter: Filter | None = None
    responsive: Expression | None = None
    selfFilterEnabled: Expression | None = None
    selfFilter: Filter | None = None
    orientation: Expression | None = None
    outlineColor: Expression | None = None
    outlineWeight: Expression | None = None


class GeneralProperties(LayoutNode):
    properties: GeneralPropertiesHelper


class DataPropertiesHelper(LayoutNode):
    endDate: Expression | None = None
    isInvertedSelectionMode: Expression | None = None
    mode: Expression | None = None
    numericEnd: Expression | None = None
    numericStart: Expression | None = None
    startDate: Expression | None = None


class DataProperties(LayoutNode):
    properties: DataPropertiesHelper


class ItemPropertiesHelper(LayoutNode):
    background: Expression | None = None
    fontColor: Expression | None = None
    fontFamily: Expression | None = None
    outline: Expression | None = None
    outlineColor: Expression | None = None
    textSize: Expression | None = None


class ItemProperties(LayoutNode):
    properties: ItemPropertiesHelper = Field(default_factory=ItemPropertiesHelper)


class DatePropertiesHelper(LayoutNode):
    background: Expression | None = None
    fontColor: Expression | None = None
    fontFamily: Expression | None = None
    textSize: Expression | None = None


class DateProperties(LayoutNode):
    properties: DatePropertiesHelper


class SliderPropertiesHelper(LayoutNode):
    color: Expression | None = None
    show: Expression | None = None


class SliderProperties(LayoutNode):
    properties: SliderPropertiesHelper


class SelectionPropertiesHelper(LayoutNode):
    selectAllCheckboxEnabled: Expression | None = None
    singleSelect: Expression | None = None
    strictSingleSelect: Expression | None = None


class SelectionProperties(LayoutNode):
    properties: SelectionPropertiesHelper


class NumericInputStylePropertiesHelper(LayoutNode):
    background: Expression | None = None
    fontColor: Expression | None = None
    fontFamily: Expression | None = None
    textSize: Expression | None = None


class NumericInputStyleProperties(LayoutNode):
    properties: NumericInputStylePropertiesHelper


class SlicerProperties(LayoutNode):
    date: list[DateProperties] | None = None
    data: list[DataProperties] | None = None
    general: list[GeneralProperties] | None = None
    header: list[HeaderProperties] = Field(default_factory=lambda: [HeaderProperties()])
    items: list[ItemProperties] = Field(default_factory=lambda: [ItemProperties()])
    numericInputStyle: list[NumericInputStyleProperties] | None = None
    selection: list[SelectionProperties] | None = None
    slider: list[SliderProperties] | None = None


class Slicer(BaseVisual):
    visualType: str = "slicer"
    model_config = ConfigDict(extra="forbid")
    columnProperties: dict[str, ColumnProperty] | None = None
    syncGroup: SyncGroup | None = None
    cachedFilterDisplayItems: list[CachedFilterDisplayItems] | None = None
    expansionStates: list[ExpansionState] | None = None
    objects: SlicerProperties = Field(default_factory=SlicerProperties)
