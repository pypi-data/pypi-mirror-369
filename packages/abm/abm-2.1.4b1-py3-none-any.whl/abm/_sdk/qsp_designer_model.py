from dataclasses import dataclass
from pathlib import Path
from typing import Literal
from uuid import UUID

from serialite import AbstractSerializableMixin, abstract_serializable, field, serializable

from .ode_model import OdeModel


#######################################################
# Dosing
#######################################################
@abstract_serializable
@dataclass(frozen=True)
class DosingScheduleState:
    dose_amount: str
    dose_duration: str | None
    is_rate: bool


@serializable
@dataclass(frozen=True)
class SingleDoseScheduleState(DosingScheduleState):
    start_time: str


@serializable
@dataclass(frozen=True)
class RegularDosesScheduleState(DosingScheduleState):
    start_time: str
    number_doses: str
    interval: str


@serializable
@dataclass(frozen=True)
class CustomDoseScheduleState(DosingScheduleState):
    dose_times: str


@abstract_serializable
@dataclass(frozen=True)
class DoseStateBase:
    pass


@serializable
@dataclass(frozen=True)
class BolusDoseState(DoseStateBase):
    amount: str
    unit: str | None


@serializable
@dataclass(frozen=True)
class GeneralBolusDoseState(DoseStateBase):
    amount: str


@serializable
@dataclass(frozen=True)
class GeneralInfusionState(DoseStateBase):
    infusion_rate: str
    duration: str


#######################################################
# Units
#######################################################
@serializable
@dataclass(frozen=True)
class BaseUnitState:
    symbol: str


@serializable
@dataclass(frozen=True)
class PrefixState:
    symbol: str
    definition: float


@serializable
@dataclass(frozen=True)
class NamedDerivedUnitState:
    symbol: str
    definition: str


@serializable
@dataclass(frozen=True)
class SimulationBaseUnitsState:
    base_unit_id: UUID
    simulation_base_unit: str


#######################################################
# Indices
#######################################################
@serializable
@dataclass(frozen=True)
class IndexIndexValuePairState:
    index_id: UUID
    index_value: int


@serializable
@dataclass(frozen=True)
class IndexRelativeValueState:
    id: UUID
    offset: int | None = None
    offset_wraps: bool | None = None
    index_value: str | None = None
    index_value_variable: str | None = None


@serializable
@dataclass(frozen=True)
class MultipleIndicesKeyState:
    pairs: list[IndexIndexValuePairState]
    runtime_pairs: list[IndexRelativeValueState]


@serializable
@dataclass(frozen=True)
class MultipleIndicesKeyValuePairStateFloat:
    key_state: MultipleIndicesKeyState
    value: float


@serializable
@dataclass(frozen=True)
class MultipleIndicesKeyValueCollectionStateFloat:
    index_ids: list[UUID]
    pairs: list[MultipleIndicesKeyValuePairStateFloat]


@serializable
@dataclass(frozen=True)
class MultipleIndicesKeyValuePairStateUuid:
    key_state: MultipleIndicesKeyState
    value: UUID


@serializable
@dataclass(frozen=True)
class MultipleIndicesKeyValueCollectionStateUuid:
    index_ids: list[UUID]
    pairs: list[MultipleIndicesKeyValuePairStateUuid]


@serializable
@dataclass(frozen=True)
class IndexCreatorIndexValuePairState:
    index_creator_id: UUID
    index_value: int


@serializable
@dataclass(frozen=True)
class MultipleIndicesKeyIndexCreatorsState:
    pairs: list[IndexCreatorIndexValuePairState]
    runtime_pairs: list[IndexRelativeValueState]


#######################################################
# Edge end types
#######################################################
@abstract_serializable
@dataclass(frozen=True)
class EdgeEndState:
    node_id: UUID


@serializable
@dataclass(frozen=True)
class NonSpecificEdgeEndState(EdgeEndState):
    each_updated_by_all: bool  # TODO: what does this mean?


@serializable
@dataclass(frozen=True)
class LegacySpecificEdgeEndState(EdgeEndState):
    key: MultipleIndicesKeyIndexCreatorsState


@serializable
@dataclass(frozen=True)
class SpecificEdgeEndState(EdgeEndState):
    component: str  # Currently assumed to be an expanded quantity name


#######################################################
# Node traits
#######################################################
@dataclass(frozen=True)
class Deactivatable:
    is_deactivated: bool


@dataclass(frozen=True)
class Exposable:
    is_exposed: bool


@dataclass(frozen=True)
class Subgraphable:
    subgraph_definition_id: UUID


#######################################################
# Abstract graph entity type
#######################################################
@dataclass(frozen=True)
class GraphEntityState(AbstractSerializableMixin):
    id: UUID


#######################################################
# Abstract node types
#######################################################
@dataclass(frozen=True)
class LocalNodeState(GraphEntityState):
    name: str


@dataclass(frozen=True)
class LocalQuantityState(LocalNodeState, Subgraphable, Exposable):
    values: MultipleIndicesKeyValueCollectionStateFloat
    unit: str | None
    attached_index_node_ids: list[UUID]
    is_output: bool


#######################################################
# Node types
#######################################################
@serializable
@dataclass(frozen=True)
class LocalAssignmentState(LocalNodeState, Subgraphable, Deactivatable):
    is_initial_only: bool
    expression: str | None  # Can be None if is_deactivated is True
    condition: str | None = None
    alternative_expression: str | None = None


@serializable
@dataclass(frozen=True)
class DosingEffectState:
    type: Literal["Dose", "Jump"]
    target: str
    expression: str


@serializable
@dataclass(frozen=True)
class LocalDosingPlanState(LocalNodeState, Subgraphable, Exposable, Deactivatable):
    dosing_schedule_state: DosingScheduleState
    effects: list[DosingEffectState]


@serializable
@dataclass(frozen=True)
class LocalEventState(LocalNodeState, Subgraphable, Exposable, Deactivatable):
    condition: str
    expression: str


@serializable
@dataclass(frozen=True)
class LocalIndexNodeState(LocalNodeState, Subgraphable):
    index_values: list[str]
    index_id: UUID
    priority: int


@serializable
@dataclass(frozen=True)
class LocalRuntimeIndexNodeState(LocalNodeState, Subgraphable):
    range_expression: str
    index_id: UUID
    priority: int


@serializable
@dataclass(frozen=True)
class LocalReactionState(LocalNodeState, Subgraphable, Exposable, Deactivatable):
    rate: str | None  # Can be None if is_deactivated is True
    reverse_rate: str | None
    index_mapping: str | None


#######################################################
# Quantity node types
#######################################################
@serializable
@dataclass(frozen=True)
class LocalCompartmentState(LocalQuantityState):
    pass


@serializable
@dataclass(frozen=True)
class LocalParameterState(LocalQuantityState):
    pass


@serializable
@dataclass(frozen=True)
class LocalSpeciesState(LocalQuantityState):
    owner_id: UUID
    is_concentration: bool = False


#######################################################
# Abstract edge types
#######################################################
@dataclass(frozen=True)
class EdgeState(GraphEntityState):
    pass


#######################################################
# Edge types
#######################################################
@serializable
@dataclass(frozen=True)
class LocalAssignmentEdgeState(EdgeState):
    direction: Literal["FromAssignment", "ToAssignment", "ToAssignmentInhibitor"]
    quantity_end: EdgeEndState
    assignment_end: EdgeEndState


@serializable
@dataclass(frozen=True)
class DosingPlanEdgeState(EdgeState):
    quantity_end: EdgeEndState
    dosing_plan_end: EdgeEndState


@serializable
@dataclass(frozen=True)
class LocalEventEdgeState(EdgeState):
    edge_type: Literal["Growth", "Product", "Modifier", "Inhibitor"]
    quantity_end: EdgeEndState
    event_end: EdgeEndState


@serializable
@dataclass(frozen=True)
class ReactionParameterEdgeState(EdgeState):
    reaction_end: EdgeEndState
    parameter_end: EdgeEndState


@serializable
@dataclass(frozen=True)
class ReactionSpeciesEdgeState(EdgeState):
    stoichiometry: str
    edge_type: Literal["Substrate", "Product", "Modifier", "Growth", "Inhibitor"]
    reaction_end: EdgeEndState
    species_end: EdgeEndState


#######################################################
# Meta edge types
#######################################################
@serializable
@dataclass(frozen=True)
class MetaEdgeState(GraphEntityState):
    from_id: UUID
    to_id: UUID


@serializable
@dataclass(frozen=True)
class WeakCloningMetaEdgeState(MetaEdgeState):
    pass


@serializable
@dataclass(frozen=True)
class LocalNonEventBasedAssignerState(LocalNodeState):
    is_initial_only: bool


@serializable
@dataclass(frozen=True)
class MultiDimensionalConstraintState(LocalNonEventBasedAssignerState, Deactivatable, Exposable, Subgraphable):
    pass


@serializable
@dataclass(frozen=True)
class LocalConstraintEdgeState(EdgeState):
    pass


@serializable
@dataclass(frozen=True)
class LocalNodeSubgraphProxyState(LocalNodeState, Subgraphable):
    subgraph_instance_id: UUID
    referenced_node_name: str | None


@serializable
@dataclass(frozen=True)
class LocalReactionSubgraphProxyState(LocalNodeSubgraphProxyState, Exposable, Deactivatable):
    pass


@serializable
@dataclass(frozen=True)
class LocalStaticIndexNodeSubgraphProxyState(LocalNodeSubgraphProxyState):
    pass


#######################################################
# Inline functions
######################################################
@serializable
@dataclass(frozen=True)
class LocalInlineFunctionState(LocalNodeState, Subgraphable):
    name: str
    arguments: list[str]
    expression: str


#######################################################
# Subgraphs
#######################################################
@serializable
@dataclass(frozen=True)
class LocalSubgraphDefinitionState(GraphEntityState, Exposable):
    name: str


@serializable
@dataclass(frozen=True)
class LocalSubgraphInstanceState(GraphEntityState, Subgraphable):  # Technically Subgraphable, but not supported here
    name: str
    definition_node_name: str
    categories_are_prefixed: bool


@serializable
@dataclass(frozen=True)
class LocalQuantitySubgraphProxyState(LocalNodeSubgraphProxyState):  # Technically Subgraphable, but not supported here
    pass


@serializable
@dataclass(frozen=True)
class LocalCompartmentSubgraphProxyState(LocalQuantitySubgraphProxyState):
    pass


@serializable
@dataclass(frozen=True)
class LocalParameterSubgraphProxyState(LocalQuantitySubgraphProxyState):
    pass


@serializable
@dataclass(frozen=True)
class LocalSpeciesSubgraphProxyState(LocalQuantitySubgraphProxyState):
    pass


#######################################################
# Imports
#######################################################
@serializable
@dataclass(frozen=True)
class WorkspaceImportState(GraphEntityState):
    name: str
    job_id: str
    import_type: Literal["Private", "Global"]


@dataclass(frozen=True)
class LocalQuantityImportState(LocalNodeState):
    workspace_import_name: str
    imported_node_name: str


@serializable
@dataclass(frozen=True)
class LocalCompartmentImportState(LocalQuantityImportState):
    pass


@serializable
@dataclass(frozen=True)
class LocalParameterImportState(LocalQuantityImportState):
    pass


@serializable
@dataclass(frozen=True)
class LocalSpeciesImportState(LocalQuantityImportState):
    pass


@serializable
@dataclass(frozen=True)
class QspDesignerModel(OdeModel):
    base_unit_states: list[BaseUnitState]
    prefix_states: list[PrefixState]
    named_derived_unit_states: list[NamedDerivedUnitState]
    simulation_base_units: list[SimulationBaseUnitsState]
    graph_entity_states: list[GraphEntityState]
    time_unit: str | None
    ignore_units: bool = False


@serializable
@dataclass(frozen=True)
class QspDesignerModelFromBytes:
    base64_content: str
    imports: dict[Path, str] = field(default_factory=dict)


# abstract_serializable only works on direct subclasses
# Recurse over subclasses to find them all
def get_all_subclasses(cls: type) -> dict[str, type]:
    subclasses = {}
    for subclass in cls.__subclasses__():
        if hasattr(subclass, "__fields_serializer__"):
            subclasses[subclass.__name__] = subclass
        subclasses.update(get_all_subclasses(subclass))
    return subclasses


GraphEntityState.__subclass_serializers__ = get_all_subclasses(GraphEntityState)
