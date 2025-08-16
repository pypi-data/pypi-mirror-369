from pydantic import ConfigDict

from pbi_core.static_files.layout._base_node import LayoutNode

from ..selector import Selector
from .base import BaseVisual
from .column_property import ColumnProperty
from .properties.base import Expression


class LegendPropertiesHelper(LayoutNode):
    position: Expression | None = None
    show: Expression | None = None


class LegendProperties(LayoutNode):
    properties: LegendPropertiesHelper


class DataPointPropertiesHelper(LayoutNode):
    fill: Expression | None = None
    showAllDataPoints: Expression | None = None


class DataPointProperties(LayoutNode):
    properties: DataPointPropertiesHelper
    selector: Selector | None = None


class LabelsPropertiesHelper(LayoutNode):
    color: Expression | None = None
    labelDisplayUnits: Expression | None = None
    labelPrecision: Expression | None = None
    labelStyle: Expression | None = None
    percentageLabelPrecision: Expression | None = None
    show: Expression | None = None


class LabelsProperties(LayoutNode):
    properties: LabelsPropertiesHelper


class PieChartProperties(LayoutNode):
    dataPoint: list[DataPointProperties] | None = None
    labels: list[LabelsProperties] | None = None
    legend: list[LegendProperties] | None = None


class PieChart(BaseVisual):
    visualType: str = "pieChart"
    model_config = ConfigDict(extra="forbid")
    columnProperties: dict[str, ColumnProperty] | None = None
    objects: PieChartProperties | None = None
