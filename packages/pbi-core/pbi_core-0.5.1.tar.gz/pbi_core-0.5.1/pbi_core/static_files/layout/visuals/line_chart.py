from pydantic import ConfigDict

from pbi_core.static_files.layout._base_node import LayoutNode
from pbi_core.static_files.layout.selector import Selector

from .base import BaseVisual
from .column_property import ColumnProperty
from .properties.base import Expression


class CategoryAxisPropertiesHelper(LayoutNode):
    axisType: Expression | None = None
    concatenateLabels: Expression | None = None
    end: Expression | None = None
    fontFamily: Expression | None = None
    fontSize: Expression | None = None
    gridlineShow: Expression | None = None
    labelColor: Expression | None = None
    maxMarginFactor: Expression | None = None
    show: Expression | None = None
    showAxisTitle: Expression | None = None
    start: Expression | None = None
    titleColor: Expression | None = None
    titleFontFamily: Expression | None = None
    titleFontSize: Expression | None = None


class CategoryAxisProperties(LayoutNode):
    properties: CategoryAxisPropertiesHelper
    selector: Selector | None = None


class LineStylesPropertiesHelper(LayoutNode):
    lineStyle: Expression | None = None
    markerColor: Expression | None = None
    markerShape: Expression | None = None
    markerSize: Expression | None = None
    showMarker: Expression | None = None
    showSeries: Expression | None = None
    stepped: Expression | None = None
    strokeLineJoin: Expression | None = None
    strokeWidth: Expression | None = None


class LineStylesProperties(LayoutNode):
    properties: LineStylesPropertiesHelper
    selector: Selector | None = None


class LabelsPropertiesHelper(LayoutNode):
    color: Expression | None = None
    labelPosition: Expression | None = None
    fontFamily: Expression | None = None
    fontSize: Expression | None = None
    labelDensity: Expression | None = None
    show: Expression | None = None
    showAll: Expression | None = None
    showSeries: Expression | None = None


class LabelsProperties(LayoutNode):
    properties: LabelsPropertiesHelper
    selector: Selector | None = None


class DataPointPropertiesHelper(LayoutNode):
    fill: Expression | None = None
    showAllDataPoints: Expression | None = None


class DataPointProperties(LayoutNode):
    properties: DataPointPropertiesHelper
    selector: Selector | None = None


class LegendPropertiesHelper(LayoutNode):
    defaultToCircle: Expression | None = None
    fontSize: Expression | None = None
    labelColor: Expression | None = None
    legendMarkerRendering: Expression | None = None
    position: Expression | None = None
    show: Expression | None = None
    showTitle: Expression | None = None
    titleText: Expression | None = None


class LegendProperties(LayoutNode):
    properties: LegendPropertiesHelper


class ValueAxisPropertiesHelper(LayoutNode):
    axisScale: Expression | None = None
    end: Expression | None = None
    fontFamily: Expression | None = None
    fontSize: Expression | None = None
    gridlineColor: Expression | None = None
    gridlineShow: Expression | None = None
    gridlineStyle: Expression | None = None
    gridlineThickness: Expression | None = None
    labelColor: Expression | None = None
    labelDensity: Expression | None = None
    labelDisplayUnits: Expression | None = None
    position: Expression | None = None
    show: Expression | None = None
    showAxisTitle: Expression | None = None
    start: Expression | None = None
    titleFontFamily: Expression | None = None
    titleText: Expression | None = None


class ValueAxisProperties(LayoutNode):
    properties: ValueAxisPropertiesHelper


class AnomalyDetectionPropertiesHelper(LayoutNode):
    confidenceBandColor: Expression | None = None
    displayName: Expression | None = None
    explainBy: Expression | None = None
    markerColor: Expression | None = None
    markerShape: Expression | None = None
    show: Expression | None = None
    transform: Expression | None = None
    transparency: Expression | None = None


class AnomalyDetectionProperties(LayoutNode):
    properties: AnomalyDetectionPropertiesHelper
    selector: Selector | None = None


class ZoomPropertiesHelper(LayoutNode):
    show: Expression | None = None
    categoryMax: Expression | None = None
    categoryMin: Expression | None = None
    valueMax: Expression | None = None
    valueMin: Expression | None = None


class ZoomProperties(LayoutNode):
    properties: ZoomPropertiesHelper


class ForecastPropertiesHelper(LayoutNode):
    show: Expression | None = None
    displayName: Expression | None = None
    lineColor: Expression | None = None
    transform: Expression | None = None


class ForecastProperties(LayoutNode):
    properties: ForecastPropertiesHelper
    selector: Selector | None = None


class PlotAreaPropertiesHelper(LayoutNode):
    transparency: Expression | None = None


class PlotAreaProperties(LayoutNode):
    properties: PlotAreaPropertiesHelper


class TrendPropertiesHelper(LayoutNode):
    displayName: Expression | None = None
    lineColor: Expression | None = None
    show: Expression | None = None


class TrendProperties(LayoutNode):
    properties: TrendPropertiesHelper


class GeneralPropertiesHelper(LayoutNode):
    responsive: Expression | None = None


class GeneralProperties(LayoutNode):
    properties: GeneralPropertiesHelper


class Y2AxisPropertiesHelper(LayoutNode):
    show: Expression | None = None


class Y2AxisProperties(LayoutNode):
    properties: Y2AxisPropertiesHelper


class Y1AxisReferenceLinePropertiesHelper(LayoutNode):
    displayName: Expression | None = None
    position: Expression | None = None
    show: Expression | None = None
    style: Expression | None = None


class Y1AxisReferenceLineProperties(LayoutNode):
    properties: Y1AxisReferenceLinePropertiesHelper
    selector: Selector | None = None


class LineChartProperties(LayoutNode):
    anomalyDetection: list[AnomalyDetectionProperties] | None = None
    categoryAxis: list[CategoryAxisProperties] | None = None
    dataPoint: list[DataPointProperties] | None = None
    forecast: list[ForecastProperties] | None = None
    general: list[GeneralProperties] | None = None
    labels: list[LabelsProperties] | None = None
    legend: list[LegendProperties] | None = None
    lineStyles: list[LineStylesProperties] | None = None
    plotArea: list[PlotAreaProperties] | None = None
    trend: list[TrendProperties] | None = None
    valueAxis: list[ValueAxisProperties] | None = None
    zoom: list[ZoomProperties] | None = None
    y1AxisReferenceLine: list[Y1AxisReferenceLineProperties] | None = None
    y2Axis: list[Y2AxisProperties] | None = None


class LineChart(BaseVisual):
    visualType: str = "lineChart"
    model_config = ConfigDict(extra="forbid")

    columnProperties: dict[str, ColumnProperty] | None = None
    drillFilterOtherVisuals: bool = True
    objects: LineChartProperties | None = None
