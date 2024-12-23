"""The action definition for the RAAML toolbox."""

from gaphor.diagram.diagramtoolbox import (
    DiagramType,
    DiagramTypes,
    ElementCreateInfo,
    ToolboxDefinition,
)
from gaphor.i18n import i18nize
from gaphor.RAAML.fta.ftatoolbox import fta
from gaphor.RAAML.raaml import Hazard, Loss, Situation, TopEvent
from gaphor.RAAML.stpa.stpatoolbox import stpa
from gaphor.UML.general.generaltoolbox import general_tools
from gaphor.UML.uml import Package

raaml_toolbox_actions: ToolboxDefinition = (
    general_tools,
    fta,
    stpa,
)

raaml_diagram_types: DiagramTypes = (
    DiagramType("fta", i18nize("FTA Diagram"), (fta,)),
    DiagramType("stpa", i18nize("STPA Diagram"), (stpa,)),
)

raaml_element_types = (
    ElementCreateInfo("package", i18nize("Package"), Package, (Package,)),
    ElementCreateInfo("topevent", i18nize("Top Event"), TopEvent, (Package,)),
    ElementCreateInfo("loss", i18nize("Loss"), Loss, (Package,)),
    ElementCreateInfo("hazard", i18nize("Hazard"), Hazard, (Package,)),
    ElementCreateInfo("situation", i18nize("Situation"), Situation, (Package,)),
)
