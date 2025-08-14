from pydantic import ConfigDict

from pbi_core.static_files.layout._base_node import LayoutNode
from pbi_core.static_files.layout.selector import Selector

from .base import BaseVisual
from .column_property import ColumnProperty
from .properties.base import Expression


class BackgroundPropertiesHelper(LayoutNode):
    show: Expression | None = None
    transparency: Expression | None = None


class BackgroundProperties(LayoutNode):
    properties: BackgroundPropertiesHelper


class TitlePropertiesHelper(LayoutNode):
    alignment: Expression | None = None
    fontColor: Expression | None = None
    fontSize: Expression | None = None
    show: Expression | None = None
    text: Expression | None = None


class TitleProperties(LayoutNode):
    properties: TitlePropertiesHelper


class GeneralPropertiesHelper(LayoutNode):
    altText: Expression | None = None


class GeneralProperties(LayoutNode):
    properties: GeneralPropertiesHelper


class LegendPropertiesHelper(LayoutNode):
    fontSize: Expression | None = None
    labelColor: Expression | None = None
    position: Expression | None = None
    show: Expression | None = None
    showTitle: Expression | None = None


class LegendProperties(LayoutNode):
    properties: LegendPropertiesHelper


class LabelsPropertiesHelper(LayoutNode):
    background: Expression | None = None
    color: Expression | None = None
    fontFamily: Expression | None = None
    fontSize: Expression | None = None
    labelDisplayUnits: Expression | None = None
    labelStyle: Expression | None = None
    overflow: Expression | None = None
    percentageLabelPrecision: Expression | None = None
    position: Expression | None = None
    show: Expression | None = None


class LabelsProperties(LayoutNode):
    properties: LabelsPropertiesHelper


class DataPointPropertiesHelper(LayoutNode):
    fill: Expression | None = None


class DataPointProperties(LayoutNode):
    properties: DataPointPropertiesHelper
    selector: Selector | None = None


class SlicesPropertiesHelper(LayoutNode):
    innerRadiusRatio: Expression | None = None


class SlicesProperties(LayoutNode):
    properties: SlicesPropertiesHelper


class DonutChartProperties(LayoutNode):
    background: list[BackgroundProperties] | None = None
    dataPoint: list[DataPointProperties] | None = None
    general: list[GeneralProperties] | None = None
    labels: list[LabelsProperties] | None = None
    legend: list[LegendProperties] | None = None
    slices: list[SlicesProperties] | None = None
    title: list[TitleProperties] | None = None


class DonutChart(BaseVisual):
    visualType: str = "donutChart"
    model_config = ConfigDict(extra="forbid")

    columnProperties: dict[str, ColumnProperty] | None = None
    drillFilterOtherVisuals: bool = True
    objects: DonutChartProperties | None = None
