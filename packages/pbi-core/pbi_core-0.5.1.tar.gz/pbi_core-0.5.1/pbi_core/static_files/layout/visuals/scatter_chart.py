from pydantic import ConfigDict

from pbi_core.static_files.layout._base_node import LayoutNode
from pbi_core.static_files.layout.selector import Selector

from .base import BaseVisual
from .column_property import ColumnProperty
from .properties.base import Expression


class DataPointPropertiesHelper(LayoutNode):
    fill: Expression | None = None
    fillRule: Expression | None = None
    legend: Expression | None = None
    showAllDataPoints: Expression | None = None
    valueAxis: Expression | None = None


class DataPointProperties(LayoutNode):
    properties: DataPointPropertiesHelper
    selector: Selector | None = None


class ValueAxisPropertiesHelper(LayoutNode):
    alignZeros: Expression | None = None
    axisScale: Expression | None = None
    end: Expression | None = None
    fontSize: Expression | None = None
    gridlineColor: Expression | None = None
    gridlineShow: Expression | None = None
    labelColor: Expression | None = None
    logAxisScale: Expression | None = None
    show: Expression | None = None
    showAxisTitle: Expression | None = None
    start: Expression | None = None
    switchAxisPosition: Expression | None = None
    titleColor: Expression | None = None
    titleFontFamily: Expression | None = None
    titleFontSize: Expression | None = None
    titleText: Expression | None = None
    treatNullsAsZero: Expression | None = None


class ValueAxisProperties(LayoutNode):
    properties: ValueAxisPropertiesHelper


class LegendPropertiesHelper(LayoutNode):
    fontSize: Expression | None = None
    labelColor: Expression | None = None
    position: Expression | None = None
    show: Expression | None = None
    showGradientLegend: Expression | None = None
    showTitle: Expression | None = None
    titleText: Expression | None = None


class LegendProperties(LayoutNode):
    properties: LegendPropertiesHelper


class FillPointPropertiesHelper(LayoutNode):
    show: Expression | None = None
    style: Expression | None = None


class FillPointProperties(LayoutNode):
    properties: FillPointPropertiesHelper


class ColorBorderPropertiesHelper(LayoutNode):
    show: Expression | None = None


class ColorBorderProperties(LayoutNode):
    properties: ColorBorderPropertiesHelper


class CategoryAxisPropertiesHelper(LayoutNode):
    axisScale: Expression | None = None
    end: Expression | None = None
    fontFamily: Expression | None = None
    fontSize: Expression | None = None
    gridlineColor: Expression | None = None
    gridlineShow: Expression | None = None
    gridlineStyle: Expression | None = None
    innerPadding: Expression | None = None
    labelColor: Expression | None = None
    logAxisScale: Expression | None = None
    maxMarginFactor: Expression | None = None
    show: Expression | None = None
    showAxisTitle: Expression | None = None
    start: Expression | None = None
    titleColor: Expression | None = None
    titleFontFamily: Expression | None = None
    titleFontSize: Expression | None = None
    titleText: Expression | None = None
    treatNullsAsZero: Expression | None = None


class CategoryAxisProperties(LayoutNode):
    properties: CategoryAxisPropertiesHelper


class BubblesPropertiesHelper(LayoutNode):
    bubbleSize: Expression | None = None
    markerShape: Expression | None = None
    showSeries: Expression | None = None


class BubblesProperties(LayoutNode):
    properties: BubblesPropertiesHelper
    selector: Selector | None = None


class Y1AxisReferenceLinePropertiesHelper(LayoutNode):
    displayName: Expression | None = None
    lineColor: Expression | None = None
    show: Expression | None = None
    value: Expression | None = None


class Y1AxisReferenceLineProperties(LayoutNode):
    properties: Y1AxisReferenceLinePropertiesHelper
    selector: Selector | None = None


class CategoryLabelsPropertiesHelper(LayoutNode):
    color: Expression | None = None
    enableBackground: Expression | None = None
    fontFamily: Expression | None = None
    fontSize: Expression | None = None
    show: Expression | None = None


class CategoryLabelsProperties(LayoutNode):
    properties: CategoryLabelsPropertiesHelper


class GeneralPropertiesHelper(LayoutNode):
    responsive: Expression | None = None


class GeneralProperties(LayoutNode):
    properties: GeneralPropertiesHelper


class PlotAreaPropertiesHelper(LayoutNode):
    transparency: Expression | None = None


class PlotAreaProperties(LayoutNode):
    properties: PlotAreaPropertiesHelper


class ScatterChartProperties(LayoutNode):
    bubbles: list[BubblesProperties] | None = None
    categoryAxis: list[CategoryAxisProperties] | None = None
    categoryLabels: list[CategoryLabelsProperties] | None = None
    colorBorder: list[ColorBorderProperties] | None = None
    dataPoint: list[DataPointProperties] | None = None
    fillPoint: list[FillPointProperties] | None = None
    general: list[GeneralProperties] | None = None
    legend: list[LegendProperties] | None = None
    plotArea: list[PlotAreaProperties] | None = None
    valueAxis: list[ValueAxisProperties] | None = None
    y1AxisReferenceLine: list[Y1AxisReferenceLineProperties] | None = None


class ScatterChart(BaseVisual):
    visualType: str = "scatterChart"
    model_config = ConfigDict(extra="forbid")

    columnProperties: dict[str, ColumnProperty] | None = None
    drillFilterOtherVisuals: bool = True
    objects: ScatterChartProperties | None = None
