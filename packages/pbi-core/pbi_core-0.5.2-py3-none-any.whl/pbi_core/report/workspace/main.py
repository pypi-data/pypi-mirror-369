from pbi_core.report.base import BaseReport
from pbi_core.ssas.server import BaseTabularModel


class WorkspaceReport(BaseReport):
    ssas: BaseTabularModel
