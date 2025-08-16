from .logging import get_logger
from .ssas.model_tables.column import Column
from .ssas.model_tables.measure import Measure
from .static_files.model_references import ModelColumnReference, ModelMeasureReference

logger = get_logger()


def column_finder(c: Column, reference: ModelColumnReference) -> bool:
    return c.explicit_name == reference.column and c.table().name == reference.table


def measure_finder(m: Measure, reference: ModelMeasureReference) -> bool:
    return m.name == reference.measure and m.table().name == reference.table
