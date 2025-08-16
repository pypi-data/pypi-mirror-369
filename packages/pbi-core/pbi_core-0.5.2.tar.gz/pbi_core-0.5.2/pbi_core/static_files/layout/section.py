from enum import Enum, IntEnum
from typing import TYPE_CHECKING, Annotated, Any, Literal
from uuid import UUID

from pydantic import ConfigDict, Json, StringConstraints, model_validator

from pbi_core.lineage.main import LineageNode
from pbi_core.static_files.model_references import ModelColumnReference, ModelMeasureReference

from ._base_node import LayoutNode
from .filters import PageFilter
from .performance import Performance, get_performance
from .selector import Selector
from .sources import Source
from .visual_container import VisualContainer

if TYPE_CHECKING:
    from pbi_core.ssas.server.tabular_model.tabular_model import BaseTabularModel, LocalTabularModel
    from pbi_core.static_files.layout import Layout


class DisplayOption(IntEnum):
    DEPRECATED_DYNAMIC = -1
    """No dynamic page without width or height.
    Deprecated: Use other display options."""
    FIT_TO_PAGE = 0
    """Page is scaled so both width and height fit on the current viewport."""
    FIT_TO_WIDTH = 1
    """Only width is scaled to fit on the current viewport, height will be updated to maintain page aspect ratio."""
    ACTUAL_SIZE = 2
    """No scaling is done - page is centered relative to the report canvas."""
    ACTUAL_SIZE_TOP_LEFT = 3
    """No scaling is done - page is anchored to top-left corder relative to the report canvas.
    Deprecated: Use ActualSize instead."""


class SectionVisibility(IntEnum):
    VISIBLE = 0
    HIDDEN = 1


class SectionConfig(LayoutNode):
    visibility: SectionVisibility = SectionVisibility.VISIBLE
    model_config = ConfigDict(extra="allow")


class BindingType(Enum):
    DEFAULT = "Default"
    """No specific usage of this binding."""
    DRILL_THROUGH = "Drillthrough"
    """Binding to be used as drillthrough."""
    TOOLTIP = "Tooltip"
    """Binding to be used as tooltip page."""


class ReferenceScope(Enum):
    DEFAULT = "Default"
    """Scope is restricted to the report."""
    CROSS_REPORT = "CrossReport"
    """Scope is across reports - for cross-report drillthrough."""


class AcceptsFilterContext(Enum):
    DEFAULT = "Default"
    """Flows filter context"""
    NONE = "None"
    """Additional filter context does not flow to the binding."""


class BindingParameter(LayoutNode):
    name: str
    """Name of the parameter - unique across the report."""
    boundFilter: str | None = None
    """Name of the filter which this parameter affects."""
    asAggregation: bool = False
    """The parameter should be applied when the field of the filter is aggregated."""
    qnaSingleSelectRequired: bool = False
    """Exactly one instance value should be picked as a filter for this parameter."""
    fieldExpr: Source | None = None
    """Field expression for page binding"""


class PageBinding(LayoutNode):
    name: str
    """Name of this binding - unique across the report."""
    type: BindingType
    """Specific usage of this binding (for example drillthrough)."""
    referenceScope: ReferenceScope | None = None
    """What is the scope under which the binding applies."""
    parameters: list[BindingParameter] | None = None
    """Additional parameters to apply when the binding is invoked."""
    acceptsFilterContext: AcceptsFilterContext | None = None
    """Should additional filter context flow when applying the binding."""


class PageInformationProperties(LayoutNode):
    pageInformationName: Any = None
    pageInformationQnaPodEnabled: Any = None
    pageInformationAltName: Any = None
    pageInformationType: Any = None


class PageInformation(LayoutNode):
    selector: Selector | None = None
    """Defines the scope at which to apply the formatting for this object.
    Can also define rules for matching highlighted values and how multiple definitions for the same property should
    be ordered."""
    propeties: PageInformationProperties
    """Describes the properties of the object to apply formatting changes to."""


class PageSizeProperties(LayoutNode):
    pageSizeTypes: Any = None
    pageSizeWidth: Any = None
    pageSizeHeight: Any = None


class PageSize(LayoutNode):
    selector: Selector | None = None
    properties: PageSizeProperties


class PageSizeObjects(LayoutNode):
    pageInformation: list[PageInformation]
    pageSize: list[PageSize]


class BackgroundProperties(LayoutNode):
    color: Any = None
    image: Any = None
    transparency: Any = None


class Background(LayoutNode):
    selector: Selector | None = None
    properties: BackgroundProperties


class DisplayAreaProperties(LayoutNode):
    verticalAlignment: Any = None


class DisplayArea(LayoutNode):
    selector: Selector | None = None
    properties: DisplayAreaProperties


class OutspacePaneProperties(LayoutNode):
    backgroundColor: Any = None
    transparency: Any = None
    foregroundColor: Any = None
    titleSize: Any = None
    searchTextSize: Any = None
    headerSize: Any = None
    fontFamily: Any = None
    border: Any = None
    borderColor: Any = None
    checkboxAndApplyColor: Any = None
    inputBoxColor: Any = None
    width: Any = None


class OutspacePane(LayoutNode):
    selector: Selector | None = None
    properties: OutspacePaneProperties


class FilterCardProperties(LayoutNode):
    backgroundColor: Any = None
    transparency: Any = None
    border: Any = None
    borderColor: Any = None
    foregroundColor: Any = None
    textSize: Any = None
    fontFamily: Any = None
    inputBoxColor: Any = None


class FilterCard(LayoutNode):
    selector: Selector | None = None
    properties: FilterCardProperties


class PageRefreshProperties(LayoutNode):
    show: Any = None
    refreshType: Any = None
    duration: Any = None
    dialogLauncher: Any = None
    measure: Any = None
    checkEvery: Any = None


class PageRefresh(LayoutNode):
    selector: Selector | None = None
    properties: PageRefreshProperties


class PersonalizeVisualProperties(LayoutNode):
    show: Any = None
    perspectiveRef: Any = None
    applyToAllPages: Any = None


class PersonalizeVisual(LayoutNode):
    selector: Selector | None = None
    properties: PersonalizeVisualProperties


class PageFormattingObjects(LayoutNode):
    pageInformation: list[PageInformation]
    pageSize: list[PageSize]
    background: list[Background]
    displayArea: list[DisplayArea]
    outspace: list[Background]  # not a typo, this matches the json schema
    outspacePane: list[OutspacePane]
    filterCard: list[FilterCard]
    pageRefresh: list[PageRefresh]
    personalizeVisuals: list[PersonalizeVisual]


class PageType(Enum):
    DRILL_THROUGH = "Drillthrough"
    """Page to be used as drillthrough."""
    TOOLTIP = "Tooltip"
    """Page to be used as tooltip."""


class PageVisibility(Enum):
    ALWAYS_VISIBLE = "AlwaysVisible"
    """Page is always shown in the pages list"""
    HIDDEN_IN_VIEW_MODE = "HiddenInViewMode"
    """Page is not visible when viewing report in View mode."""


class VisualInteractionFilterType(Enum):
    DEFAULT = "Default"
    """The target visual type determines if it should accept the interaction as a highlight or as a filter."""
    DATA_FILTER = "DataFilter"
    """Data point selection is added as a filter to the target visual."""
    HIGHLIGHT_FILTER = "HighlightFilter"
    """Data point selection is added as a highlight to the target visual."""
    NO_FILTER = "NoFilter"
    """Data point selection is ignored by the target visual."""


class VisualInteraction(LayoutNode):
    source: str
    """Visual name that will be the source of user interaction (selecting data point for example)."""
    target: str
    """Visual name for the target of the interaction (selecting data point for example)."""
    type: VisualInteractionFilterType
    """How should the interaction flow from source to target visual (as highlights, as filter, none)."""


class QuickExploreVisualContainerConfig(LayoutNode):
    name: str
    """Name of the visual - matches the name property in visual.json files"""
    fields: list[Source]
    """Specific data fields used to build this visual from the full set of selected fields"""


class QuickExploreRelatedLayout(LayoutNode):
    version: Literal[1] = 1
    dataTableName: str | None = None
    """If data table is shown, then the name of that visual"""


class QuickExploreCombinationLayout(LayoutNode):
    version: Literal[1] = 1
    dataTableName: str | None = None
    """If data table is shown, then the name of that visual"""


class QuickExploreLayoutContainer(LayoutNode):
    related: QuickExploreRelatedLayout
    """A layout that has 1 hero visual and some related visuals"""
    combination: QuickExploreCombinationLayout
    """Layout that generates visuals purely based on combination of fields
    Deprecated: Use related layout instead."""


class AutoPageGenerationConfig(LayoutNode):
    selectedFields: list[Source]
    """Data fields to use for the auto page generation"""
    visualContainerConfigurations: list[QuickExploreVisualContainerConfig]
    """Visuals already on the page previously generated by the auto-config"""
    layout: QuickExploreLayoutContainer | None = None
    """The specific layout chosen to render the auto-visuals"""


class PageHowCreated(Enum):
    DEFAULT = "Default"
    """Page is generated by user interaction."""
    COPILOT = "Copilot"
    """Page is created by copilot."""


class Annotation(LayoutNode):
    name: str
    """Unique name for the annotation."""
    value: str
    """A value for this annotation."""


class Section(LayoutNode):
    _layout: "Layout | None"
    """The layout the section is associated with, if it exists"""
    height: int
    """Height of the page (in pixels) - optional only for 'DeprecatedDynamic' option, required otherwise."""
    width: int
    """Width of the page (in pixels) - optional only for 'DeprecatedDynamic' option, required otherwise."""
    displayOption: DisplayOption
    """Defines how the page is scaled."""
    config: Json[SectionConfig]
    objectId: UUID | None = None
    visualContainers: list[VisualContainer]
    ordinal: int = 0
    filters: Json[list[PageFilter]]
    """Filters that apply to all the visuals on this page - on top of the filters defined for the whole report."""
    displayName: str
    """A user facing name for this page."""
    name: Annotated[str, StringConstraints(max_length=50)]
    """A unique identifier for the page across the whole report."""
    id: int | None = None
    pageBinding: PageBinding | None = None
    """Additional metadata defined for how this page is used (tooltip, drillthrough, etc)."""
    objects: PageFormattingObjects | None = None
    """Defines the formatting for different objects on a page."""
    type: PageType | None = None
    """Specific usage of this page (for example drillthrough)."""
    visibility: PageVisibility | None = PageVisibility.ALWAYS_VISIBLE
    """Defines when this page should be visible - by default it is always visible."""
    visualInteractions: list[VisualInteraction] | None = None
    """Defines how data point selection on a specific visual flow (as filters) to other visuals on the page.
    By default it is up-to the visual to apply it either as a cross-highlight or as a filter."""
    autoPageGenerationConfig: AutoPageGenerationConfig | None = None
    """Configuration that was used to automatically generate a page (for example using 'Auto create the report'
    option)."""
    annotations: list[Annotation] | None = None
    """Additional information to be saved (for example comments, readme, etc) for this page."""
    howCreated: PageHowCreated | None = None
    """Source of creation of this page."""

    def pbi_core_name(self) -> str:
        return self.name

    def get_ssas_elements(
        self,
        *,
        include_visuals: bool = True,
        include_filters: bool = True,
    ) -> set[ModelColumnReference | ModelMeasureReference]:
        """Returns the SSAS elements (columns and measures) this report page is directly dependent on."""
        ret: set[ModelColumnReference | ModelMeasureReference] = set()
        if include_visuals:
            for viz in self.visualContainers:
                ret.update(viz.get_ssas_elements())
        if include_filters:
            for f in self.filters:
                ret.update(f.get_ssas_elements())
        return ret

    def get_lineage(
        self,
        lineage_type: Literal["children", "parents"],
        tabular_model: "BaseTabularModel",
    ) -> LineageNode:
        if lineage_type == "children":
            return LineageNode(self, lineage_type)

        page_filters = self.get_ssas_elements()

        report_filters = set()
        if self._layout is not None:
            report_filters = self._layout.get_ssas_elements(include_sections=False)

        entities = page_filters | report_filters
        children_nodes = [ref.to_model(tabular_model) for ref in entities]

        children_lineage = [p.get_lineage(lineage_type) for p in children_nodes if p is not None]
        return LineageNode(self, lineage_type, children_lineage)

    def get_performance(self, model: "LocalTabularModel", *, clear_cache: bool = False) -> list[Performance]:
        """Calculates various metrics on the speed of the visual.

        Current Metrics:
            Total Seconds to Query
            Total Rows Retrieved

        Raises:
            ValueError: If the page does not have any querying visuals.

        """
        commands: list[str] = []
        for viz in self.visualContainers:
            if viz.query is not None:
                command = viz._get_data_command()
                if command is not None:
                    commands.append(command.get_dax(model).dax)
        if not commands:
            msg = "Cannot get performance for a page without any querying visuals"
            raise ValueError(msg)
        return get_performance(model, commands, clear_cache=clear_cache)

    @model_validator(mode="after")
    def update_sections(self) -> "Section":
        for viz in self.visualContainers:
            viz._section = self
        return self
