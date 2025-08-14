# Mapping from luminarycloud vis enums to LCVis equivalent values

import logging
from luminarycloud.enum import Representation, FieldComponent

logger = logging.getLogger(__name__)


def representation_to_lcvis(representation: Representation) -> int:
    if representation == Representation.SURFACE:
        return 0
    if representation == Representation.SURFACE_WITH_EDGES:
        return 1
    if representation == Representation.WIREFRAME:
        return 2
    logger.error(f"{representation} is not supported by LCVis")
    return 0


def field_component_to_lcvis(comp: FieldComponent) -> int:
    if comp == FieldComponent.X:
        return 0
    if comp == FieldComponent.Y:
        return 1
    if comp == FieldComponent.Z:
        return 2
    if comp == FieldComponent.MAGNITUDE:
        return 3
    logger.error(f"Invalid FieldComponent {comp}")
    return 0
