from typing import Annotated, Any

from pydantic import Discriminator, Tag

from .action_button import ActionButton
from .bar_chart import BarChart
from .basic_shape import BasicShape
from .card import Card
from .clustered_column_chart import ClusteredColumnChart
from .column_chart import ColumnChart
from .donut_chart import DonutChart
from .funnel import Funnel
from .generic import GenericVisual
from .image import Image
from .line_chart import LineChart
from .line_stacked_column_combo_chart import LineStackedColumnComboChart
from .pie_chart import PieChart
from .scatter_chart import ScatterChart
from .slicer import Slicer
from .table import TableChart
from .text_box import TextBox


def get_visual(v: object | dict[str, Any]) -> str:
    if isinstance(v, dict):
        assert "visualType" in v
        assert isinstance(v["visualType"], str)

        mapping = {
            "actionButton": "ActionButton",
            "barChart": "BarChart",
            "basicShape": "BasicShape",
            "card": "Card",
            "clusteredColumnChart": "ClusteredColumnChart",
            "columnChart": "ColumnChart",
            "donutChart": "DonutChart",
            "funnel": "Funnel",
            "image": "Image",
            "lineChart": "LineChart",
            "lineStackedColumnComboChart": "LineStackedColumnComboChart",
            "pieChart": "PieChart",
            "scatterChart": "ScatterChart",
            "slicer": "Slicer",
            "tableEx": "TableChart",
            "textbox": "TextBox",
        }
        return mapping.get(v["visualType"], "GenericVisual")
    return v.__class__.__name__


Visual = Annotated[
    Annotated[ActionButton, Tag("ActionButton")]
    | Annotated[BarChart, Tag("BarChart")]
    | Annotated[GenericVisual, Tag("GenericVisual")]
    | Annotated[BasicShape, Tag("BasicShape")]
    | Annotated[Card, Tag("Card")]
    | Annotated[ColumnChart, Tag("ColumnChart")]
    | Annotated[ClusteredColumnChart, Tag("ClusteredColumnChart")]
    | Annotated[DonutChart, Tag("DonutChart")]
    | Annotated[Funnel, Tag("Funnel")]
    | Annotated[Image, Tag("Image")]
    | Annotated[LineChart, Tag("LineChart")]
    | Annotated[LineStackedColumnComboChart, Tag("LineStackedColumnComboChart")]
    | Annotated[PieChart, Tag("PieChart")]
    | Annotated[ScatterChart, Tag("ScatterChart")]
    | Annotated[Slicer, Tag("Slicer")]
    | Annotated[TableChart, Tag("TableChart")]
    | Annotated[TextBox, Tag("TextBox")],
    Discriminator(get_visual),
]


__all__ = ["GenericVisual", "Visual"]
