from pydantic import ConfigDict

from pbi_core.static_files.layout._base_node import LayoutNode
from pbi_core.static_files.layout.selector import Selector

from .base import BaseVisual
from .column_property import ColumnProperty
from .properties.base import Expression


class DataPointPropertiesHelper(LayoutNode):
    fill: Expression | None = None
    fillRule: Expression | None = None
    showAllDataPoints: Expression | None = None


class DataPointProperties(LayoutNode):
    properties: DataPointPropertiesHelper
    selector: Selector | None = None


class LabelsPropertiesHelper(LayoutNode):
    backgroundColor: Expression | None = None
    backgroundTransparency: Expression | None = None
    color: Expression | None = None
    enableBackground: Expression | None = None
    fontSize: Expression | None = None
    labelDisplayUnits: Expression | None = None
    labelOrientation: Expression | None = None
    labelPosition: Expression | None = None
    show: Expression | None = None
    showAll: Expression | None = None


class LabelsProperties(LayoutNode):
    properties: LabelsPropertiesHelper
    selector: Selector | None = None


class LegendPropertiesHelper(LayoutNode):
    legendMarkerRendering: Expression | None = None
    position: Expression | None = None
    show: Expression | None = None


class LegendProperties(LayoutNode):
    properties: LegendPropertiesHelper
    selector: Selector | None = None


class LineStylesPropertiesHelper(LayoutNode):
    lineStyle: Expression | None = None
    markerShape: Expression | None = None
    shadeArea: Expression | None = None
    showMarker: Expression | None = None
    showSeries: Expression | None = None
    stepped: Expression | None = None
    strokeWidth: Expression | None = None


class LineStylesProperties(LayoutNode):
    properties: LineStylesPropertiesHelper
    selector: Selector | None = None


class ValueAxisPropertiesHelper(LayoutNode):
    alignZeros: Expression | None = None
    end: Expression | None = None
    gridlineShow: Expression | None = None
    secEnd: Expression | None = None
    secShow: Expression | None = None
    secStart: Expression | None = None
    start: Expression | None = None
    show: Expression | None = None


class ValueAxisProperties(LayoutNode):
    properties: ValueAxisPropertiesHelper
    selector: Selector | None = None


class SubheaderPropertiesHelper(LayoutNode):
    fontSize: Expression | None = None


class SubheaderProperties(LayoutNode):
    properties: SubheaderPropertiesHelper


class SmallMultiplesLayoutPropertiesHelper(LayoutNode):
    gridLineColor: Expression | None = None
    gridLineStyle: Expression | None = None
    gridLineType: Expression | None = None
    gridPadding: Expression | None = None
    rowCount: Expression | None = None


class SmallMultiplesLayoutProperties(LayoutNode):
    properties: SmallMultiplesLayoutPropertiesHelper


class CategoryAxisPropertiesHelper(LayoutNode):
    axisType: Expression | None = None


class CategoryAxisProperties(LayoutNode):
    properties: CategoryAxisPropertiesHelper


class LineStackedColumnComboChartProperties(LayoutNode):
    categoryAxis: list[CategoryAxisProperties] | None = None
    dataPoint: list[DataPointProperties] | None = None
    labels: list[LabelsProperties] | None = None
    legend: list[LegendProperties] | None = None
    lineStyles: list[LineStylesProperties] | None = None
    smallMultiplesLayout: list[SmallMultiplesLayoutProperties] | None = None
    subheader: list[SubheaderProperties] | None = None
    valueAxis: list[ValueAxisProperties] | None = None


class LineStackedColumnComboChart(BaseVisual):
    visualType: str = "lineStackedColumnComboChart"
    model_config = ConfigDict(extra="forbid")

    columnProperties: dict[str, ColumnProperty] | None = None
    drillFilterOtherVisuals: bool = True
    objects: LineStackedColumnComboChartProperties | None = None
