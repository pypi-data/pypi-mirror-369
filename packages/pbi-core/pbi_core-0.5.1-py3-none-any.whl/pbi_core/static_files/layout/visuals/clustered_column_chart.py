from pydantic import ConfigDict

from pbi_core.static_files.layout._base_node import LayoutNode
from pbi_core.static_files.layout.selector import Selector

from .base import BaseVisual
from .column_property import ColumnProperty
from .properties.base import Expression


class LabelsPropertiesHelper(LayoutNode):
    backgroundTransparency: Expression | None = None
    color: Expression | None = None
    enableBackground: Expression | None = None
    fontFamily: Expression | None = None
    fontSize: Expression | None = None
    labelDisplayUnits: Expression | None = None
    labelOrientation: Expression | None = None
    labelOverflow: Expression | None = None
    labelPosition: Expression | None = None
    labelPrecision: Expression | None = None
    show: Expression | None = None
    showAll: Expression | None = None


class LabelsProperties(LayoutNode):
    properties: LabelsPropertiesHelper
    selector: Selector | None = None


class ValueAxisPropertiesHelper(LayoutNode):
    axisScale: Expression | None = None
    fontFamily: Expression | None = None
    fontSize: Expression | None = None
    gridlineShow: Expression | None = None
    labelColor: Expression | None = None
    labelDisplayUnits: Expression | None = None
    logAxisScale: Expression | None = None
    show: Expression | None = None
    showAxisTitle: Expression | None = None
    start: Expression | None = None
    titleFontFamily: Expression | None = None


class ValueAxisProperties(LayoutNode):
    properties: ValueAxisPropertiesHelper
    selector: Selector | None = None


class DataPointPropertiesHelper(LayoutNode):
    fill: Expression | None = None
    showAllDataPoints: Expression | None = None


class DataPointProperties(LayoutNode):
    properties: DataPointPropertiesHelper
    selector: Selector | None = None


class CategoryAxisPropertiesHelper(LayoutNode):
    axisType: Expression | None = None
    concatenateLabels: Expression | None = None
    fontFamily: Expression | None = None
    fontSize: Expression | None = None
    gridlineShow: Expression | None = None
    gridlineStyle: Expression | None = None
    innerPadding: Expression | None = None
    labelColor: Expression | None = None
    maxMarginFactor: Expression | None = None
    preferredCategoryWidth: Expression | None = None
    show: Expression | None = None
    showAxisTitle: Expression | None = None
    titleColor: Expression | None = None
    titleFontSize: Expression | None = None


class CategoryAxisProperties(LayoutNode):
    properties: CategoryAxisPropertiesHelper


class LegendPropertiesHelper(LayoutNode):
    fontSize: Expression | None = None
    labelColor: Expression | None = None
    position: Expression | None = None
    show: Expression | None = None
    showTitle: Expression | None = None


class LegendProperties(LayoutNode):
    properties: LegendPropertiesHelper


class TrendPropertiesHelper(LayoutNode):
    displayName: Expression | None = None
    lineColor: Expression | None = None
    show: Expression | None = None


class TrendProperties(LayoutNode):
    properties: TrendPropertiesHelper


class PlotAreaPropertiesHelper(LayoutNode):
    transparency: Expression | None = None


class PlotAreaProperties(LayoutNode):
    properties: PlotAreaPropertiesHelper


class GeneralPropertiesHelper(LayoutNode):
    responsive: Expression | None = None


class GeneralProperties(LayoutNode):
    properties: GeneralPropertiesHelper


class ClusteredColumnChartProperties(LayoutNode):
    categoryAxis: list[CategoryAxisProperties] | None = None
    dataPoint: list[DataPointProperties] | None = None
    general: list[GeneralProperties] | None = None
    labels: list[LabelsProperties] | None = None
    legend: list[LegendProperties] | None = None
    plotArea: list[PlotAreaProperties] | None = None
    trend: list[TrendProperties] | None = None
    valueAxis: list[ValueAxisProperties] | None = None


class ClusteredColumnChart(BaseVisual):
    visualType: str = "clusteredColumnChart"
    model_config = ConfigDict(extra="forbid")

    columnProperties: dict[str, ColumnProperty] | None = None
    drillFilterOtherVisuals: bool = True
    objects: ClusteredColumnChartProperties | None = None
