"""SQLAlchemy models generated from DPM by the OpenDPM project."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import (
    BOOLEAN,
    INTEGER,
    VARCHAR,
    Column,
    ForeignKey,
)
from sqlalchemy import (
    Table as AlchemyTable,
)
from sqlalchemy.orm import DeclarativeMeta, Mapped, mapped_column, relationship

if TYPE_CHECKING:
    from datetime import date, datetime
    from decimal import Decimal


# We use DeclarativeMeta instead of DeclarativeBase
# to be compatible with mypy and __mapper_args__
class DPM(metaclass=DeclarativeMeta):
    """Base class for all DPM models."""


class AuxCellMapping(DPM):
    """Auto-generated model for the Aux_CellMapping table."""

    __tablename__ = "Aux_CellMapping"

    new_cell_id: Mapped[int] = mapped_column("NewCellID", primary_key=True)
    new_table_vid: Mapped[int] = mapped_column("NewTableVID", primary_key=True)
    old_cell_id: Mapped[int] = mapped_column("OldCellID")
    old_table_vid: Mapped[int] = mapped_column("OldTableVID")


class AuxCellStatus(DPM):
    """Auto-generated model for the Aux_CellStatus table."""

    __tablename__ = "Aux_CellStatus"

    table_vid: Mapped[int] = mapped_column("TableVID", primary_key=True)
    cell_id: Mapped[int] = mapped_column("CellID", primary_key=True)
    status: Mapped[str] = mapped_column("Status")
    is_new_cell: Mapped[bool] = mapped_column("IsNewCell")


class Concept(DPM):
    """Auto-generated model for the Concept table."""

    __tablename__ = "Concept"

    # We quote the references to avoid circular dependencies
    concept_guid: Mapped[str] = mapped_column("ConceptGUID", primary_key=True)
    class_id: Mapped[int] = mapped_column("ClassID", ForeignKey("DPMClass.class_id"))
    owner_id: Mapped[int] = mapped_column("OwnerID", ForeignKey("Organisation.org_id"))

    class_: Mapped[DPMClass] = relationship(foreign_keys=class_id)
    owner: Mapped[Organisation] = relationship(foreign_keys=owner_id)


class DPMClass(DPM):
    """Auto-generated model for the DPMClass table."""

    __tablename__ = "DPMClass"

    class_id: Mapped[int] = mapped_column("ClassID", primary_key=True)
    name: Mapped[str] = mapped_column("Name")
    type: Mapped[str | None] = mapped_column("Type")
    owner_class_id: Mapped[int | None] = mapped_column(
        "OwnerClassID",
        ForeignKey(class_id),
    )
    has_references: Mapped[bool] = mapped_column("HasReferences")

    owner_class: Mapped[DPMClass | None] = relationship(foreign_keys=owner_class_id)


class DataType(DPM):
    """Auto-generated model for the DataType table."""

    __tablename__ = "DataType"

    data_type_id: Mapped[int] = mapped_column("DataTypeID", primary_key=True)
    code: Mapped[str] = mapped_column("Code")
    name: Mapped[str] = mapped_column("Name")
    parent_data_type_id: Mapped[int | None] = mapped_column(
        "ParentDataTypeID",
        ForeignKey(data_type_id),
    )
    is_active: Mapped[bool] = mapped_column("IsActive")

    parent_data_type: Mapped[DataType | None] = relationship(
        foreign_keys=parent_data_type_id,
    )


class Language(DPM):
    """Auto-generated model for the Language table."""

    __tablename__ = "Language"

    language_code: Mapped[int] = mapped_column("LanguageCode", primary_key=True)
    name: Mapped[str] = mapped_column("Name")


ModelViolations = AlchemyTable(
    "ModelViolations",
    DPM.metadata,
    Column("ViolationCode", VARCHAR, nullable=False),
    Column("Violation", VARCHAR, nullable=False),
    Column("isBlocking", BOOLEAN, nullable=False),
    Column("TableVID", INTEGER),
    Column("OldTableVID", INTEGER),
    Column("TableCode", VARCHAR),
    Column("HeaderID", INTEGER),
    Column("HeaderCode", VARCHAR),
    Column("HeaderVID", INTEGER),
    Column("OldHeaderVID", INTEGER),
    Column("KeyHeader", INTEGER),
    Column("HeaderDirection", VARCHAR),
    Column("HeaderPropertyID", INTEGER),
    Column("HeaderPropertyCode", VARCHAR),
    Column("HeaderSubcategoryID", INTEGER),
    Column("HeaderSubcategoryName", VARCHAR),
    Column("HeaderContextID", INTEGER),
    Column("CategoryID", INTEGER),
    Column("CategoryCode", VARCHAR),
    Column("ItemID", INTEGER),
    Column("ItemCode", VARCHAR),
    Column("CellID", INTEGER),
    Column("CellCode", VARCHAR),
    Column("Cell2ID", INTEGER),
    Column("Cell2Code", VARCHAR),
    Column("VVEndReleaseID", INTEGER),
    Column("NewAspect", VARCHAR),
)


class Operator(DPM):
    """Auto-generated model for the Operator table."""

    __tablename__ = "Operator"

    operator_id: Mapped[int] = mapped_column("OperatorID", primary_key=True)
    name: Mapped[str] = mapped_column("Name")
    symbol: Mapped[str] = mapped_column("Symbol")
    type: Mapped[str] = mapped_column("Type")


class Organisation(DPM):
    """Auto-generated model for the Organisation table."""

    __tablename__ = "Organisation"

    org_id: Mapped[int] = mapped_column("OrgID", primary_key=True)
    name: Mapped[str] = mapped_column("Name")
    acronym: Mapped[str] = mapped_column("Acronym")
    id_prefix: Mapped[int] = mapped_column("IDPrefix")
    row_guid: Mapped[str] = mapped_column("RowGUID", ForeignKey(Concept.concept_guid))

    unique_concept: Mapped[Concept] = relationship(foreign_keys=row_guid)


class Role(DPM):
    """Auto-generated model for the Role table."""

    __tablename__ = "Role"

    role_id: Mapped[int] = mapped_column("RoleID", primary_key=True)
    name: Mapped[str] = mapped_column("Name")


class SubdivisionType(DPM):
    """Auto-generated model for the SubdivisionType table."""

    __tablename__ = "SubdivisionType"

    subdivision_type_id: Mapped[int] = mapped_column(
        "SubdivisionTypeID",
        primary_key=True,
    )
    name: Mapped[str] = mapped_column("Name")
    description: Mapped[str] = mapped_column("Description")


VarGenerationDetail = AlchemyTable(
    "VarGeneration_Detail",
    DPM.metadata,
    Column("noofcells", INTEGER, nullable=False),
    Column("NewAspect", VARCHAR, nullable=False),
    Column("ModuleVID", INTEGER, nullable=False),
    Column("ModuleCode", VARCHAR, nullable=False),
    Column("TableCode", VARCHAR, nullable=False),
    Column("TableVID", INTEGER, nullable=False),
    Column("CellID", INTEGER, nullable=False),
    Column("cellcode", VARCHAR, nullable=False),
    Column("outcomeID", VARCHAR, nullable=False),
    Column("outcomeVID", VARCHAR, nullable=False),
    Column("ReportMsg", VARCHAR, nullable=False),
    Column("isVoid", BOOLEAN, nullable=False),
    Column("tvstartReleaseID", INTEGER, nullable=False),
    Column("mvStartReleaseID", INTEGER, nullable=False),
    Column("vvOldEndReleaseID", INTEGER),
    Column("OldAspect", VARCHAR, nullable=False),
    Column("IsNewCell", BOOLEAN, nullable=False),
    Column("isnewPropertyDataType", BOOLEAN, nullable=False),
    Column("isNewKey", BOOLEAN, nullable=False),
    Column("OldVariableID", INTEGER),
    Column("NewVarID", INTEGER, nullable=False),
    Column("OldVariableVID", INTEGER),
    Column("NewVVID", INTEGER, nullable=False),
)

VarGenerationSummary = AlchemyTable(
    "VarGeneration_Summary",
    DPM.metadata,
    Column("outcomeid", VARCHAR, nullable=False),
    Column("outcomevid", VARCHAR, nullable=False),
    Column("ReportMsg", VARCHAR, nullable=False),
    Column("noofcells", INTEGER, nullable=False),
    Column("mincell", VARCHAR, nullable=False),
    Column("maxcell", VARCHAR, nullable=False),
)


class CompoundKey(DPM):
    """Auto-generated model for the CompoundKey table."""

    __tablename__ = "CompoundKey"

    key_id: Mapped[int] = mapped_column("KeyID", primary_key=True)
    signature: Mapped[str] = mapped_column("Signature")
    row_guid: Mapped[str | None] = mapped_column(
        "RowGUID",
        ForeignKey(Concept.concept_guid),
    )

    unique_concept: Mapped[Concept | None] = relationship(foreign_keys=row_guid)


class ConceptRelation(DPM):
    """Auto-generated model for the ConceptRelation table."""

    __tablename__ = "ConceptRelation"

    concept_relation_id: Mapped[int] = mapped_column(
        "ConceptRelationID",
        primary_key=True,
    )
    type: Mapped[str] = mapped_column("Type")
    row_guid: Mapped[str] = mapped_column("RowGUID", ForeignKey(Concept.concept_guid))

    unique_concept: Mapped[Concept] = relationship(foreign_keys=row_guid)


class Context(DPM):
    """Auto-generated model for the Context table."""

    __tablename__ = "Context"

    context_id: Mapped[int] = mapped_column("ContextID", primary_key=True)
    signature: Mapped[str] = mapped_column("Signature")
    row_guid: Mapped[str | None] = mapped_column(
        "RowGUID",
        ForeignKey(Concept.concept_guid),
    )

    unique_concept: Mapped[Concept | None] = relationship(foreign_keys=row_guid)


class DPMAttribute(DPM):
    """Auto-generated model for the DPMAttribute table."""

    __tablename__ = "DPMAttribute"

    attribute_id: Mapped[int] = mapped_column("AttributeID", primary_key=True)
    class_id: Mapped[int] = mapped_column("ClassID", ForeignKey(DPMClass.class_id))
    name: Mapped[str] = mapped_column("Name")
    has_translations: Mapped[bool] = mapped_column("HasTranslations")

    class_: Mapped[DPMClass] = relationship(foreign_keys=class_id)


class Document(DPM):
    """Auto-generated model for the Document table."""

    __tablename__ = "Document"

    document_id: Mapped[int] = mapped_column("DocumentID", primary_key=True)
    name: Mapped[str] = mapped_column("Name")
    code: Mapped[str] = mapped_column("Code")
    type: Mapped[str] = mapped_column("Type")
    org_id: Mapped[int] = mapped_column("OrgID", ForeignKey(Organisation.org_id))
    row_guid: Mapped[str] = mapped_column("RowGUID", ForeignKey(Concept.concept_guid))

    org: Mapped[Organisation] = relationship(foreign_keys=org_id)
    unique_concept: Mapped[Concept] = relationship(foreign_keys=row_guid)


class Framework(DPM):
    """Auto-generated model for the Framework table."""

    __tablename__ = "Framework"

    framework_id: Mapped[int] = mapped_column("FrameworkID", primary_key=True)
    code: Mapped[str] = mapped_column("Code")
    name: Mapped[str] = mapped_column("Name")
    description: Mapped[str | None] = mapped_column("Description")
    row_guid: Mapped[str] = mapped_column("RowGUID", ForeignKey(Concept.concept_guid))

    unique_concept: Mapped[Concept] = relationship(foreign_keys=row_guid)


class Item(DPM):
    """Auto-generated model for the Item table."""

    __tablename__ = "Item"

    item_id: Mapped[int] = mapped_column("ItemID", primary_key=True)
    name: Mapped[str] = mapped_column("Name")
    description: Mapped[str | None] = mapped_column("Description")
    is_property: Mapped[bool] = mapped_column("IsProperty")
    is_active: Mapped[bool] = mapped_column("IsActive")
    row_guid: Mapped[str | None] = mapped_column(
        "RowGUID",
        ForeignKey(Concept.concept_guid),
    )

    unique_concept: Mapped[Concept | None] = relationship(foreign_keys=row_guid)


class Operation(DPM):
    """Auto-generated model for the Operation table."""

    __tablename__ = "Operation"

    operation_id: Mapped[int] = mapped_column("OperationID", primary_key=True)
    code: Mapped[str] = mapped_column("Code")
    type: Mapped[str] = mapped_column("Type")
    source: Mapped[str] = mapped_column("Source")
    group_oper_id: Mapped[int | None] = mapped_column(
        "GroupOperID",
        ForeignKey(operation_id),
    )
    row_guid: Mapped[str] = mapped_column("RowGUID", ForeignKey(Concept.concept_guid))

    group_oper: Mapped[Operation | None] = relationship(foreign_keys=group_oper_id)
    unique_concept: Mapped[Concept] = relationship(foreign_keys=row_guid)


class OperatorArgument(DPM):
    """Auto-generated model for the OperatorArgument table."""

    __tablename__ = "OperatorArgument"

    argument_id: Mapped[int] = mapped_column("ArgumentID", primary_key=True)
    operator_id: Mapped[int] = mapped_column(
        "OperatorID",
        ForeignKey(Operator.operator_id),
    )
    order: Mapped[int] = mapped_column("Order")
    is_mandatory: Mapped[bool] = mapped_column("IsMandatory")
    name: Mapped[str] = mapped_column("Name")

    operator: Mapped[Operator] = relationship(foreign_keys=operator_id)


class Release(DPM):
    """Auto-generated model for the Release table."""

    __tablename__ = "Release"

    release_id: Mapped[int] = mapped_column("ReleaseID", primary_key=True)
    code: Mapped[str] = mapped_column("Code")
    date: Mapped[date] = mapped_column("Date")
    description: Mapped[str | None] = mapped_column("Description")
    status: Mapped[str] = mapped_column("Status")
    is_current: Mapped[bool] = mapped_column("IsCurrent")
    row_guid: Mapped[str] = mapped_column("RowGUID", ForeignKey(Concept.concept_guid))
    latest_variable_gen_time: Mapped[datetime | None] = mapped_column(
        "LatestVariableGenTime",
    )

    unique_concept: Mapped[Concept] = relationship(foreign_keys=row_guid)


class Table(DPM):
    """Auto-generated model for the Table table."""

    __tablename__ = "Table"

    table_id: Mapped[int] = mapped_column("TableID", primary_key=True)
    is_abstract: Mapped[bool] = mapped_column("IsAbstract")
    has_open_columns: Mapped[bool] = mapped_column("HasOpenColumns")
    has_open_rows: Mapped[bool] = mapped_column("HasOpenRows")
    has_open_sheets: Mapped[bool] = mapped_column("HasOpenSheets")
    is_normalised: Mapped[bool] = mapped_column("IsNormalised")
    is_flat: Mapped[bool] = mapped_column("IsFlat")
    row_guid: Mapped[str] = mapped_column("RowGUID", ForeignKey(Concept.concept_guid))

    unique_concept: Mapped[Concept] = relationship(foreign_keys=row_guid)


class User(DPM):
    """Auto-generated model for the User table."""

    __tablename__ = "User"

    user_id: Mapped[int] = mapped_column("UserID", primary_key=True)
    org_id: Mapped[int] = mapped_column("OrgID", ForeignKey(Organisation.org_id))
    name: Mapped[str] = mapped_column("Name")

    org: Mapped[Organisation] = relationship(foreign_keys=org_id)


class Variable(DPM):
    """Auto-generated model for the Variable table."""

    __tablename__ = "Variable"

    variable_id: Mapped[int] = mapped_column("VariableID", primary_key=True)
    type: Mapped[str] = mapped_column("Type")
    row_guid: Mapped[str | None] = mapped_column(
        "RowGUID",
        ForeignKey(Concept.concept_guid),
    )

    unique_concept: Mapped[Concept | None] = relationship(foreign_keys=row_guid)


class Category(DPM):
    """Auto-generated model for the Category table."""

    __tablename__ = "Category"

    category_id: Mapped[int] = mapped_column("CategoryID", primary_key=True)
    code: Mapped[str] = mapped_column("Code")
    name: Mapped[str] = mapped_column("Name")
    description: Mapped[str | None] = mapped_column("Description")
    is_enumerated: Mapped[bool] = mapped_column("IsEnumerated")
    is_active: Mapped[bool] = mapped_column("IsActive")
    is_external_ref_data: Mapped[bool] = mapped_column("IsExternalRefData")
    ref_data_source: Mapped[str | None] = mapped_column("RefDataSource")
    row_guid: Mapped[str] = mapped_column("RowGUID", ForeignKey(Concept.concept_guid))
    created_release: Mapped[int] = mapped_column(
        "CreatedRelease",
        ForeignKey(Release.release_id),
    )

    unique_concept: Mapped[Concept] = relationship(foreign_keys=row_guid)
    release: Mapped[Release] = relationship(foreign_keys=created_release)


class ChangeLog(DPM):
    """Auto-generated model for the ChangeLog table."""

    __tablename__ = "ChangeLog"

    row_guid: Mapped[str] = mapped_column(
        "RowGUID",
        ForeignKey(Concept.concept_guid),
        primary_key=True,
    )
    class_id: Mapped[int] = mapped_column(
        "ClassID",
        ForeignKey(DPMClass.class_id),
        primary_key=True,
    )
    attribute_id: Mapped[int] = mapped_column(
        "AttributeID",
        ForeignKey(DPMAttribute.attribute_id),
        primary_key=True,
    )
    timestamp: Mapped[int] = mapped_column("Timestamp", primary_key=True)
    old_value: Mapped[str] = mapped_column("OldValue")
    new_value: Mapped[str] = mapped_column("NewValue")
    change_type: Mapped[str] = mapped_column("ChangeType")
    status: Mapped[str] = mapped_column("Status")
    user_id: Mapped[int] = mapped_column("UserID", ForeignKey(User.user_id))
    release_id: Mapped[int] = mapped_column("ReleaseID", ForeignKey(Release.release_id))

    unique_concept: Mapped[Concept] = relationship(foreign_keys=row_guid)
    class_: Mapped[DPMClass] = relationship(foreign_keys=class_id)
    attribute: Mapped[DPMAttribute] = relationship(foreign_keys=attribute_id)
    user: Mapped[User] = relationship(foreign_keys=user_id)
    release: Mapped[Release] = relationship(foreign_keys=release_id)


class CompoundItemContext(DPM):
    """Auto-generated model for the CompoundItemContext table."""

    __tablename__ = "CompoundItemContext"

    item_id: Mapped[int] = mapped_column(
        "ItemID",
        ForeignKey(Item.item_id),
        primary_key=True,
    )
    start_release_id: Mapped[int] = mapped_column(
        "StartReleaseID",
        ForeignKey(Release.release_id),
        primary_key=True,
    )
    context_id: Mapped[int] = mapped_column("ContextID", ForeignKey(Context.context_id))
    end_release_id: Mapped[int | None] = mapped_column(
        "EndReleaseID",
        ForeignKey(Release.release_id),
    )
    row_guid: Mapped[str] = mapped_column("RowGUID", ForeignKey(Concept.concept_guid))

    start_release: Mapped[Release] = relationship(foreign_keys=start_release_id)
    end_release: Mapped[Release | None] = relationship(foreign_keys=end_release_id)
    unique_concept: Mapped[Concept] = relationship(foreign_keys=row_guid)
    item: Mapped[Item] = relationship(foreign_keys=item_id)
    context: Mapped[Context] = relationship(foreign_keys=context_id)


class DocumentVersion(DPM):
    """Auto-generated model for the DocumentVersion table."""

    __tablename__ = "DocumentVersion"

    document_vid: Mapped[int] = mapped_column("DocumentVID", primary_key=True)
    document_id: Mapped[int] = mapped_column(
        "DocumentID",
        ForeignKey(Document.document_id),
    )
    code: Mapped[str] = mapped_column("Code")
    version: Mapped[str] = mapped_column("Version")
    publication_date: Mapped[date] = mapped_column("PublicationDate")
    row_guid: Mapped[str] = mapped_column("RowGUID", ForeignKey(Concept.concept_guid))

    unique_concept: Mapped[Concept] = relationship(foreign_keys=row_guid)
    document: Mapped[Document] = relationship(foreign_keys=document_id)


class Header(DPM):
    """Auto-generated model for the Header table."""

    __tablename__ = "Header"

    header_id: Mapped[int] = mapped_column("HeaderID", primary_key=True)
    table_id: Mapped[int] = mapped_column("TableID", ForeignKey(Table.table_id))
    direction: Mapped[str] = mapped_column("Direction")
    is_key: Mapped[bool] = mapped_column("IsKey")
    row_guid: Mapped[str] = mapped_column("RowGUID", ForeignKey(Concept.concept_guid))
    is_attribute: Mapped[bool] = mapped_column("IsAttribute")

    unique_concept: Mapped[Concept] = relationship(foreign_keys=row_guid)
    table: Mapped[Table] = relationship(foreign_keys=table_id)


class Module(DPM):
    """Auto-generated model for the Module table."""

    __tablename__ = "Module"

    module_id: Mapped[int] = mapped_column("ModuleID", primary_key=True)
    framework_id: Mapped[int] = mapped_column(
        "FrameworkID",
        ForeignKey(Framework.framework_id),
    )
    row_guid: Mapped[str | None] = mapped_column(
        "RowGUID",
        ForeignKey(Concept.concept_guid),
    )
    is_document_module: Mapped[bool] = mapped_column("isDocumentModule")

    unique_concept: Mapped[Concept | None] = relationship(foreign_keys=row_guid)
    framework: Mapped[Framework] = relationship(foreign_keys=framework_id)


class OperationCodePrefix(DPM):
    """Auto-generated model for the OperationCodePrefix table."""

    __tablename__ = "OperationCodePrefix"

    operation_code_prefix_id: Mapped[int] = mapped_column(
        "OperationCodePrefixID",
        primary_key=True,
    )
    code: Mapped[str] = mapped_column("Code")
    list_name: Mapped[str] = mapped_column("ListName")
    framework_id: Mapped[int] = mapped_column(
        "FrameworkID",
        ForeignKey(Framework.framework_id),
    )

    framework: Mapped[Framework] = relationship(foreign_keys=framework_id)


class OperationVersion(DPM):
    """Auto-generated model for the OperationVersion table."""

    __tablename__ = "OperationVersion"

    operation_vid: Mapped[int] = mapped_column("OperationVID", primary_key=True)
    operation_id: Mapped[int] = mapped_column(
        "OperationID",
        ForeignKey(Operation.operation_id),
    )
    precondition_operation_vid: Mapped[int | None] = mapped_column(
        "PreconditionOperationVID",
        ForeignKey(operation_vid),
    )
    severity_operation_vid: Mapped[int | None] = mapped_column(
        "SeverityOperationVID",
        ForeignKey(operation_vid),
    )
    start_release_id: Mapped[int] = mapped_column(
        "StartReleaseID",
        ForeignKey(Release.release_id),
    )
    end_release_id: Mapped[int | None] = mapped_column(
        "EndReleaseID",
        ForeignKey(Release.release_id),
    )
    expression: Mapped[str] = mapped_column("Expression")
    description: Mapped[str | None] = mapped_column("Description")
    row_guid: Mapped[str] = mapped_column("RowGUID", ForeignKey(Concept.concept_guid))
    endorsement: Mapped[str | None] = mapped_column("Endorsement")
    is_variant_approved: Mapped[bool | None] = mapped_column("IsVariantApproved")

    precondition_operation_version: Mapped[OperationVersion | None] = relationship(
        foreign_keys=precondition_operation_vid,
    )
    severity_operation_version: Mapped[OperationVersion | None] = relationship(
        foreign_keys=severity_operation_vid,
    )
    start_release: Mapped[Release] = relationship(foreign_keys=start_release_id)
    end_release: Mapped[Release | None] = relationship(foreign_keys=end_release_id)
    unique_concept: Mapped[Concept] = relationship(foreign_keys=row_guid)
    operation: Mapped[Operation] = relationship(foreign_keys=operation_id)


class Property(DPM):
    """Auto-generated model for the Property table."""

    __tablename__ = "Property"

    property_id: Mapped[int] = mapped_column(
        "PropertyID",
        ForeignKey(Item.item_id),
        primary_key=True,
    )
    is_composite: Mapped[bool] = mapped_column("IsComposite")
    is_metric: Mapped[bool] = mapped_column("IsMetric")
    data_type_id: Mapped[int] = mapped_column(
        "DataTypeID",
        ForeignKey(DataType.data_type_id),
    )
    value_length: Mapped[int | None] = mapped_column("ValueLength")
    period_type: Mapped[str | None] = mapped_column("PeriodType")
    row_guid: Mapped[str] = mapped_column("RowGUID", ForeignKey(Concept.concept_guid))

    item: Mapped[Item] = relationship(foreign_keys=property_id)
    unique_concept: Mapped[Concept] = relationship(foreign_keys=row_guid)
    data_type: Mapped[DataType] = relationship(foreign_keys=data_type_id)


class RelatedConcept(DPM):
    """Auto-generated model for the RelatedConcept table."""

    __tablename__ = "RelatedConcept"

    concept_guid: Mapped[str] = mapped_column(
        "ConceptGUID",
        ForeignKey(Concept.concept_guid),
        primary_key=True,
    )
    concept_relation_id: Mapped[int] = mapped_column(
        "ConceptRelationID",
        ForeignKey(ConceptRelation.concept_relation_id),
        primary_key=True,
    )
    is_related_concept: Mapped[bool] = mapped_column("IsRelatedConcept")
    row_guid: Mapped[str | None] = mapped_column(
        "RowGUID",
        ForeignKey(Concept.concept_guid),
    )

    unique_concept: Mapped[Concept | None] = relationship(foreign_keys=row_guid)
    concept: Mapped[Concept] = relationship(foreign_keys=concept_guid)
    concept_relation: Mapped[ConceptRelation] = relationship(
        foreign_keys=concept_relation_id,
    )


class TableGroup(DPM):
    """Auto-generated model for the TableGroup table."""

    __tablename__ = "TableGroup"

    table_group_id: Mapped[int] = mapped_column("TableGroupID", primary_key=True)
    code: Mapped[str] = mapped_column("Code")
    name: Mapped[str] = mapped_column("Name")
    description: Mapped[str | None] = mapped_column("Description")
    type: Mapped[str] = mapped_column("Type")
    row_guid: Mapped[str] = mapped_column("RowGUID", ForeignKey(Concept.concept_guid))
    start_release_id: Mapped[int] = mapped_column(
        "StartReleaseID",
        ForeignKey(Release.release_id),
    )
    end_release_id: Mapped[int | None] = mapped_column(
        "EndReleaseID",
        ForeignKey(Release.release_id),
    )
    parent_table_group_id: Mapped[int | None] = mapped_column(
        "ParentTableGroupID",
        ForeignKey(table_group_id),
    )

    unique_concept: Mapped[Concept] = relationship(foreign_keys=row_guid)
    start_release: Mapped[Release] = relationship(foreign_keys=start_release_id)
    end_release: Mapped[Release | None] = relationship(foreign_keys=end_release_id)
    parent_table_group: Mapped[TableGroup | None] = relationship(
        foreign_keys=parent_table_group_id,
    )


class Translation(DPM):
    """Auto-generated model for the Translation table."""

    __tablename__ = "Translation"

    concept_guid: Mapped[str] = mapped_column(
        "ConceptGUID",
        ForeignKey(Concept.concept_guid),
        primary_key=True,
    )
    attribute_id: Mapped[int] = mapped_column(
        "AttributeID",
        ForeignKey(DPMAttribute.attribute_id),
        primary_key=True,
    )
    translator_id: Mapped[int] = mapped_column(
        "TranslatorID",
        ForeignKey(Organisation.org_id),
        primary_key=True,
    )
    language_code: Mapped[int] = mapped_column(
        "LanguageCode",
        ForeignKey(Language.language_code),
        primary_key=True,
    )
    translation: Mapped[str] = mapped_column("Translation")
    row_guid: Mapped[str] = mapped_column("RowGUID", ForeignKey(Concept.concept_guid))

    attribute: Mapped[DPMAttribute] = relationship(foreign_keys=attribute_id)
    translator: Mapped[Organisation] = relationship(foreign_keys=translator_id)
    language: Mapped[Language] = relationship(foreign_keys=language_code)
    unique_concept: Mapped[Concept] = relationship(foreign_keys=row_guid)
    concept: Mapped[Concept] = relationship(foreign_keys=concept_guid)


class UserRole(DPM):
    """Auto-generated model for the UserRole table."""

    __tablename__ = "UserRole"

    user_id: Mapped[int] = mapped_column(
        "UserID",
        ForeignKey(User.user_id),
        primary_key=True,
    )
    role_id: Mapped[int] = mapped_column(
        "RoleID",
        ForeignKey(Role.role_id),
        primary_key=True,
    )

    user: Mapped[User] = relationship(foreign_keys=user_id)
    role: Mapped[Role] = relationship(foreign_keys=role_id)


class VariableGeneration(DPM):
    """Auto-generated model for the VariableGeneration table."""

    __tablename__ = "VariableGeneration"

    variable_generation_id: Mapped[int] = mapped_column(
        "VariableGenerationID",
        primary_key=True,
    )
    start_date: Mapped[datetime] = mapped_column("StartDate")
    end_date: Mapped[datetime | None] = mapped_column("EndDate")
    status: Mapped[str] = mapped_column("Status")
    release_id: Mapped[int] = mapped_column("ReleaseID", ForeignKey(Release.release_id))
    error: Mapped[str | None] = mapped_column("Error")

    release: Mapped[Release] = relationship(foreign_keys=release_id)


class Cell(DPM):
    """Auto-generated model for the Cell table."""

    __tablename__ = "Cell"

    cell_id: Mapped[int] = mapped_column("CellID", primary_key=True)
    table_id: Mapped[int] = mapped_column("TableID", ForeignKey(Table.table_id))
    column_id: Mapped[int] = mapped_column("ColumnID", ForeignKey(Header.header_id))
    row_id: Mapped[int | None] = mapped_column("RowID", ForeignKey(Header.header_id))
    sheet_id: Mapped[int | None] = mapped_column(
        "SheetID",
        ForeignKey(Header.header_id),
    )
    row_guid: Mapped[str] = mapped_column("RowGUID", ForeignKey(Concept.concept_guid))

    column: Mapped[Header] = relationship(foreign_keys=column_id)
    row: Mapped[Header | None] = relationship(foreign_keys=row_id)
    sheet: Mapped[Header | None] = relationship(foreign_keys=sheet_id)
    unique_concept: Mapped[Concept] = relationship(foreign_keys=row_guid)
    table: Mapped[Table] = relationship(foreign_keys=table_id)


class ContextComposition(DPM):
    """Auto-generated model for the ContextComposition table."""

    __tablename__ = "ContextComposition"

    context_id: Mapped[int] = mapped_column(
        "ContextID",
        ForeignKey(Context.context_id),
        primary_key=True,
    )
    property_id: Mapped[int] = mapped_column(
        "PropertyID",
        ForeignKey(Property.property_id),
        primary_key=True,
    )
    item_id: Mapped[int] = mapped_column("ItemID", ForeignKey(Item.item_id))
    row_guid: Mapped[str | None] = mapped_column(
        "RowGUID",
        ForeignKey(Concept.concept_guid),
    )

    unique_concept: Mapped[Concept | None] = relationship(foreign_keys=row_guid)
    context: Mapped[Context] = relationship(foreign_keys=context_id)
    property: Mapped[Property] = relationship(foreign_keys=property_id)
    item: Mapped[Item] = relationship(foreign_keys=item_id)


class ItemCategory(DPM):
    """Auto-generated model for the ItemCategory table."""

    __tablename__ = "ItemCategory"

    item_id: Mapped[int] = mapped_column(
        "ItemID",
        ForeignKey(Item.item_id),
        primary_key=True,
    )
    start_release_id: Mapped[int] = mapped_column(
        "StartReleaseID",
        ForeignKey(Release.release_id),
        primary_key=True,
    )
    category_id: Mapped[int] = mapped_column(
        "CategoryID",
        ForeignKey(Category.category_id),
    )
    code: Mapped[str] = mapped_column("Code")
    is_default_item: Mapped[bool] = mapped_column("IsDefaultItem")
    signature: Mapped[str] = mapped_column("Signature")
    end_release_id: Mapped[int | None] = mapped_column(
        "EndReleaseID",
        ForeignKey(Release.release_id),
    )
    row_guid: Mapped[str | None] = mapped_column(
        "RowGUID",
        ForeignKey(Concept.concept_guid),
    )

    start_release: Mapped[Release] = relationship(foreign_keys=start_release_id)
    end_release: Mapped[Release | None] = relationship(foreign_keys=end_release_id)
    unique_concept: Mapped[Concept | None] = relationship(foreign_keys=row_guid)
    item: Mapped[Item] = relationship(foreign_keys=item_id)
    category: Mapped[Category] = relationship(foreign_keys=category_id)


class ModuleVersion(DPM):
    """Auto-generated model for the ModuleVersion table."""

    __tablename__ = "ModuleVersion"

    module_vid: Mapped[int] = mapped_column("ModuleVID", primary_key=True)
    module_id: Mapped[int] = mapped_column("ModuleID", ForeignKey(Module.module_id))
    global_key_id: Mapped[int | None] = mapped_column(
        "GlobalKeyID",
        ForeignKey(CompoundKey.key_id),
    )
    start_release_id: Mapped[int] = mapped_column(
        "StartReleaseID",
        ForeignKey(Release.release_id),
    )
    end_release_id: Mapped[int | None] = mapped_column(
        "EndReleaseID",
        ForeignKey(Release.release_id),
    )
    code: Mapped[str] = mapped_column("Code")
    name: Mapped[str] = mapped_column("Name")
    description: Mapped[str | None] = mapped_column("Description")
    version_number: Mapped[str] = mapped_column("VersionNumber")
    from_reference_date: Mapped[date] = mapped_column("FromReferenceDate")
    to_reference_date: Mapped[date | None] = mapped_column("ToReferenceDate")
    row_guid: Mapped[str | None] = mapped_column(
        "RowGUID",
        ForeignKey(Concept.concept_guid),
    )
    is_reported: Mapped[bool] = mapped_column("IsReported")
    is_calculated: Mapped[bool] = mapped_column("IsCalculated")

    global_key: Mapped[CompoundKey | None] = relationship(foreign_keys=global_key_id)
    start_release: Mapped[Release] = relationship(foreign_keys=start_release_id)
    end_release: Mapped[Release | None] = relationship(foreign_keys=end_release_id)
    unique_concept: Mapped[Concept | None] = relationship(foreign_keys=row_guid)
    module: Mapped[Module] = relationship(foreign_keys=module_id)


class OperationNode(DPM):
    """Auto-generated model for the OperationNode table."""

    __tablename__ = "OperationNode"

    node_id: Mapped[int] = mapped_column("NodeID", primary_key=True)
    operation_vid: Mapped[int] = mapped_column(
        "OperationVID",
        ForeignKey(OperationVersion.operation_vid),
    )
    parent_node_id: Mapped[int | None] = mapped_column(
        "ParentNodeID",
        ForeignKey(node_id),
    )
    operator_id: Mapped[int | None] = mapped_column(
        "OperatorID",
        ForeignKey(Operator.operator_id),
    )
    argument_id: Mapped[int | None] = mapped_column(
        "ArgumentID",
        ForeignKey(OperatorArgument.argument_id),
    )
    absolute_tolerance: Mapped[Decimal | None] = mapped_column("AbsoluteTolerance")
    relative_tolerance: Mapped[Decimal | None] = mapped_column("RelativeTolerance")
    fallback_value: Mapped[str | None] = mapped_column("FallbackValue")
    use_interval_arithmetics: Mapped[bool] = mapped_column("UseIntervalArithmetics")
    operand_type: Mapped[str | None] = mapped_column("OperandType")
    is_leaf: Mapped[bool] = mapped_column("IsLeaf")
    scalar: Mapped[str | None] = mapped_column("Scalar")

    parent_node: Mapped[OperationNode | None] = relationship(
        foreign_keys=parent_node_id,
    )
    argument: Mapped[OperatorArgument | None] = relationship(foreign_keys=argument_id)
    operation_version: Mapped[OperationVersion] = relationship(
        foreign_keys=operation_vid,
    )
    operator: Mapped[Operator | None] = relationship(foreign_keys=operator_id)


class OperationScope(DPM):
    """Auto-generated model for the OperationScope table."""

    __tablename__ = "OperationScope"

    operation_scope_id: Mapped[int] = mapped_column(
        "OperationScopeID",
        primary_key=True,
    )
    operation_vid: Mapped[int] = mapped_column(
        "OperationVID",
        ForeignKey(OperationVersion.operation_vid),
    )
    is_active: Mapped[bool] = mapped_column("IsActive")
    severity: Mapped[str] = mapped_column("Severity")
    from_submission_date: Mapped[date | None] = mapped_column("FromSubmissionDate")
    row_guid: Mapped[str] = mapped_column("RowGUID", ForeignKey(Concept.concept_guid))

    unique_concept: Mapped[Concept] = relationship(foreign_keys=row_guid)
    operation_version: Mapped[OperationVersion] = relationship(
        foreign_keys=operation_vid,
    )


class OperationVersionData(DPM):
    """Auto-generated model for the OperationVersionData table."""

    __tablename__ = "OperationVersionData"

    operation_vid: Mapped[int] = mapped_column(
        "OperationVID",
        ForeignKey(OperationVersion.operation_vid),
        primary_key=True,
    )
    error: Mapped[str | None] = mapped_column("Error")
    error_code: Mapped[str | None] = mapped_column("ErrorCode")
    is_applying: Mapped[bool] = mapped_column("IsApplying")
    proposing_status: Mapped[str | None] = mapped_column("ProposingStatus")

    operation_version: Mapped[OperationVersion] = relationship(
        foreign_keys=operation_vid,
    )


class PropertyCategory(DPM):
    """Auto-generated model for the PropertyCategory table."""

    __tablename__ = "PropertyCategory"

    property_id: Mapped[int] = mapped_column(
        "PropertyID",
        ForeignKey(Property.property_id),
        primary_key=True,
    )
    start_release_id: Mapped[int] = mapped_column(
        "StartReleaseID",
        ForeignKey(Release.release_id),
        primary_key=True,
    )
    category_id: Mapped[int] = mapped_column(
        "CategoryID",
        ForeignKey(Category.category_id),
    )
    end_release_id: Mapped[int | None] = mapped_column(
        "EndReleaseID",
        ForeignKey(Release.release_id),
    )
    row_guid: Mapped[str | None] = mapped_column(
        "RowGUID",
        ForeignKey(Concept.concept_guid),
    )

    start_release: Mapped[Release] = relationship(foreign_keys=start_release_id)
    end_release: Mapped[Release | None] = relationship(foreign_keys=end_release_id)
    unique_concept: Mapped[Concept | None] = relationship(foreign_keys=row_guid)
    property: Mapped[Property] = relationship(foreign_keys=property_id)
    category: Mapped[Category] = relationship(foreign_keys=category_id)


class SubCategory(DPM):
    """Auto-generated model for the SubCategory table."""

    __tablename__ = "SubCategory"

    sub_category_id: Mapped[int] = mapped_column("SubCategoryID", primary_key=True)
    category_id: Mapped[int] = mapped_column(
        "CategoryID",
        ForeignKey(Category.category_id),
    )
    code: Mapped[str] = mapped_column("Code")
    name: Mapped[str | None] = mapped_column("Name")
    description: Mapped[str | None] = mapped_column("Description")
    row_guid: Mapped[str] = mapped_column("RowGUID", ForeignKey(Concept.concept_guid))

    unique_concept: Mapped[Concept] = relationship(foreign_keys=row_guid)
    category: Mapped[Category] = relationship(foreign_keys=category_id)


class Subdivision(DPM):
    """Auto-generated model for the Subdivision table."""

    __tablename__ = "Subdivision"

    subdivision_id: Mapped[int] = mapped_column("SubdivisionID", primary_key=True)
    document_vid: Mapped[int] = mapped_column(
        "DocumentVID",
        ForeignKey(DocumentVersion.document_vid),
    )
    subdivision_type_id: Mapped[int] = mapped_column(
        "SubdivisionTypeID",
        ForeignKey(SubdivisionType.subdivision_type_id),
    )
    number: Mapped[str] = mapped_column("Number")
    parent_subdivision_id: Mapped[int] = mapped_column(
        "ParentSubdivisionID",
        ForeignKey(subdivision_id),
    )
    structure_path: Mapped[str] = mapped_column("StructurePath")
    text_excerpt: Mapped[str] = mapped_column("TextExcerpt")
    row_guid: Mapped[str] = mapped_column("RowGUID", ForeignKey(Concept.concept_guid))

    parent_subdivision: Mapped[Subdivision] = relationship(
        foreign_keys=parent_subdivision_id,
    )
    unique_concept: Mapped[Concept] = relationship(foreign_keys=row_guid)
    document_version: Mapped[DocumentVersion] = relationship(foreign_keys=document_vid)
    subdivision_type: Mapped[SubdivisionType] = relationship(
        foreign_keys=subdivision_type_id,
    )


class SuperCategoryComposition(DPM):
    """Auto-generated model for the SuperCategoryComposition table."""

    __tablename__ = "SuperCategoryComposition"

    super_category_id: Mapped[int] = mapped_column(
        "SuperCategoryID",
        ForeignKey(Category.category_id),
        primary_key=True,
    )
    category_id: Mapped[int] = mapped_column(
        "CategoryID",
        ForeignKey(Category.category_id),
        primary_key=True,
    )
    start_release_id: Mapped[int] = mapped_column(
        "StartReleaseID",
        ForeignKey(Release.release_id),
        primary_key=True,
    )
    end_release_id: Mapped[int | None] = mapped_column(
        "EndReleaseID",
        ForeignKey(Release.release_id),
    )
    row_guid: Mapped[str] = mapped_column("RowGUID", ForeignKey(Concept.concept_guid))

    super_category: Mapped[Category] = relationship(foreign_keys=super_category_id)
    start_release: Mapped[Release] = relationship(foreign_keys=start_release_id)
    end_release: Mapped[Release | None] = relationship(foreign_keys=end_release_id)
    unique_concept: Mapped[Concept] = relationship(foreign_keys=row_guid)
    category: Mapped[Category] = relationship(foreign_keys=category_id)


class TableGroupComposition(DPM):
    """Auto-generated model for the TableGroupComposition table."""

    __tablename__ = "TableGroupComposition"

    table_group_id: Mapped[int] = mapped_column(
        "TableGroupID",
        ForeignKey(TableGroup.table_group_id),
        primary_key=True,
    )
    table_id: Mapped[int] = mapped_column(
        "TableID",
        ForeignKey(Table.table_id),
        primary_key=True,
    )
    order: Mapped[int | None] = mapped_column("Order")
    start_release_id: Mapped[int] = mapped_column(
        "StartReleaseID",
        ForeignKey(Release.release_id),
    )
    end_release_id: Mapped[int | None] = mapped_column(
        "EndReleaseID",
        ForeignKey(Release.release_id),
    )
    row_guid: Mapped[str | None] = mapped_column(
        "RowGUID",
        ForeignKey(Concept.concept_guid),
    )

    start_release: Mapped[Release] = relationship(foreign_keys=start_release_id)
    end_release: Mapped[Release | None] = relationship(foreign_keys=end_release_id)
    unique_concept: Mapped[Concept | None] = relationship(foreign_keys=row_guid)
    table_group: Mapped[TableGroup] = relationship(foreign_keys=table_group_id)
    table: Mapped[Table] = relationship(foreign_keys=table_id)


class TableVersion(DPM):
    """Auto-generated model for the TableVersion table."""

    __tablename__ = "TableVersion"

    table_vid: Mapped[int] = mapped_column("TableVID", primary_key=True)
    code: Mapped[str] = mapped_column("Code")
    name: Mapped[str] = mapped_column("Name")
    description: Mapped[str | None] = mapped_column("Description")
    table_id: Mapped[int] = mapped_column("TableID", ForeignKey(Table.table_id))
    abstract_table_id: Mapped[int | None] = mapped_column(
        "AbstractTableID",
        ForeignKey(Table.table_id),
    )
    key_id: Mapped[int | None] = mapped_column("KeyID", ForeignKey(CompoundKey.key_id))
    property_id: Mapped[int | None] = mapped_column(
        "PropertyID",
        ForeignKey(Property.property_id),
    )
    context_id: Mapped[int | None] = mapped_column(
        "ContextID",
        ForeignKey(Context.context_id),
    )
    start_release_id: Mapped[int] = mapped_column(
        "StartReleaseID",
        ForeignKey(Release.release_id),
    )
    end_release_id: Mapped[int | None] = mapped_column(
        "EndReleaseID",
        ForeignKey(Release.release_id),
    )
    row_guid: Mapped[str] = mapped_column("RowGUID", ForeignKey(Concept.concept_guid))

    abstract_table: Mapped[Table | None] = relationship(foreign_keys=abstract_table_id)
    key: Mapped[CompoundKey | None] = relationship(foreign_keys=key_id)
    start_release: Mapped[Release] = relationship(foreign_keys=start_release_id)
    end_release: Mapped[Release | None] = relationship(foreign_keys=end_release_id)
    unique_concept: Mapped[Concept] = relationship(foreign_keys=row_guid)
    table: Mapped[Table] = relationship(foreign_keys=table_id)
    property: Mapped[Property | None] = relationship(foreign_keys=property_id)
    context: Mapped[Context | None] = relationship(foreign_keys=context_id)


class VariableCalculation(DPM):
    """Auto-generated model for the VariableCalculation table."""

    __tablename__ = "VariableCalculation"

    module_id: Mapped[int] = mapped_column(
        "ModuleID",
        ForeignKey(Module.module_id),
        primary_key=True,
    )
    variable_id: Mapped[int] = mapped_column(
        "VariableID",
        ForeignKey(Variable.variable_id),
        primary_key=True,
    )
    operation_vid: Mapped[int] = mapped_column(
        "OperationVID",
        ForeignKey(OperationVersion.operation_vid),
        primary_key=True,
    )
    from_reference_date: Mapped[date] = mapped_column("FromReferenceDate")
    to_reference_date: Mapped[date] = mapped_column("ToReferenceDate")
    row_guid: Mapped[str] = mapped_column("RowGUID", ForeignKey(Concept.concept_guid))

    unique_concept: Mapped[Concept] = relationship(foreign_keys=row_guid)
    module: Mapped[Module] = relationship(foreign_keys=module_id)
    variable: Mapped[Variable] = relationship(foreign_keys=variable_id)
    operation_version: Mapped[OperationVersion] = relationship(
        foreign_keys=operation_vid,
    )


class ModuleVersionComposition(DPM):
    """Auto-generated model for the ModuleVersionComposition table."""

    __tablename__ = "ModuleVersionComposition"

    module_vid: Mapped[int] = mapped_column(
        "ModuleVID",
        ForeignKey(ModuleVersion.module_vid),
        primary_key=True,
    )
    table_id: Mapped[int] = mapped_column(
        "TableID",
        ForeignKey(Table.table_id),
        primary_key=True,
    )
    table_vid: Mapped[int] = mapped_column(
        "TableVID",
        ForeignKey(TableVersion.table_vid),
    )
    order: Mapped[int | None] = mapped_column("Order")
    row_guid: Mapped[str] = mapped_column("RowGUID", ForeignKey(Concept.concept_guid))

    unique_concept: Mapped[Concept] = relationship(foreign_keys=row_guid)
    module_version: Mapped[ModuleVersion] = relationship(foreign_keys=module_vid)
    table: Mapped[Table] = relationship(foreign_keys=table_id)
    table_version: Mapped[TableVersion] = relationship(foreign_keys=table_vid)


class OperandReference(DPM):
    """Auto-generated model for the OperandReference table."""

    __tablename__ = "OperandReference"

    operand_reference_id: Mapped[int] = mapped_column(
        "OperandReferenceID",
        primary_key=True,
    )
    node_id: Mapped[int] = mapped_column("NodeID", ForeignKey(OperationNode.node_id))
    x: Mapped[int | None] = mapped_column("x")
    y: Mapped[int | None] = mapped_column("y")
    z: Mapped[int | None] = mapped_column("z")
    operand_reference: Mapped[str] = mapped_column("OperandReference")
    item_id: Mapped[int | None] = mapped_column("ItemID", ForeignKey(Item.item_id))
    property_id: Mapped[int | None] = mapped_column(
        "PropertyID",
        ForeignKey(Property.property_id),
    )
    variable_id: Mapped[int | None] = mapped_column(
        "VariableID",
        ForeignKey(Variable.variable_id),
    )
    sub_category_id: Mapped[int | None] = mapped_column(
        "SubCategoryID",
        ForeignKey(SubCategory.sub_category_id),
    )

    node: Mapped[OperationNode] = relationship(foreign_keys=node_id)
    item: Mapped[Item | None] = relationship(foreign_keys=item_id)
    property: Mapped[Property | None] = relationship(foreign_keys=property_id)
    variable: Mapped[Variable | None] = relationship(foreign_keys=variable_id)
    sub_category: Mapped[SubCategory | None] = relationship(
        foreign_keys=sub_category_id,
    )


class OperationScopeComposition(DPM):
    """Auto-generated model for the OperationScopeComposition table."""

    __tablename__ = "OperationScopeComposition"

    operation_scope_id: Mapped[int] = mapped_column(
        "OperationScopeID",
        ForeignKey(OperationScope.operation_scope_id),
        primary_key=True,
    )
    module_vid: Mapped[int] = mapped_column(
        "ModuleVID",
        ForeignKey(ModuleVersion.module_vid),
        primary_key=True,
    )
    row_guid: Mapped[str] = mapped_column("RowGUID", ForeignKey(Concept.concept_guid))

    unique_concept: Mapped[Concept] = relationship(foreign_keys=row_guid)
    operation_scope: Mapped[OperationScope] = relationship(
        foreign_keys=operation_scope_id,
    )
    module_version: Mapped[ModuleVersion] = relationship(foreign_keys=module_vid)


class Reference(DPM):
    """Auto-generated model for the Reference table."""

    __tablename__ = "Reference"

    subdivision_id: Mapped[int] = mapped_column(
        "SubdivisionID",
        ForeignKey(Subdivision.subdivision_id),
        primary_key=True,
    )
    concept_guid: Mapped[str] = mapped_column(
        "ConceptGUID",
        ForeignKey(Concept.concept_guid),
        primary_key=True,
    )
    row_guid: Mapped[str] = mapped_column("RowGUID", ForeignKey(Concept.concept_guid))

    unique_concept: Mapped[Concept] = relationship(foreign_keys=row_guid)
    subdivision: Mapped[Subdivision] = relationship(foreign_keys=subdivision_id)
    concept: Mapped[Concept] = relationship(foreign_keys=concept_guid)


class SubCategoryVersion(DPM):
    """Auto-generated model for the SubCategoryVersion table."""

    __tablename__ = "SubCategoryVersion"

    sub_category_vid: Mapped[int] = mapped_column("SubCategoryVID", primary_key=True)
    sub_category_id: Mapped[int] = mapped_column(
        "SubCategoryID",
        ForeignKey(SubCategory.sub_category_id),
    )
    start_release_id: Mapped[int] = mapped_column(
        "StartReleaseID",
        ForeignKey(Release.release_id),
    )
    end_release_id: Mapped[int | None] = mapped_column(
        "EndReleaseID",
        ForeignKey(Release.release_id),
    )
    row_guid: Mapped[str] = mapped_column("RowGUID", ForeignKey(Concept.concept_guid))

    start_release: Mapped[Release] = relationship(foreign_keys=start_release_id)
    end_release: Mapped[Release | None] = relationship(foreign_keys=end_release_id)
    unique_concept: Mapped[Concept] = relationship(foreign_keys=row_guid)
    sub_category: Mapped[SubCategory] = relationship(foreign_keys=sub_category_id)


class TableAssociation(DPM):
    """Auto-generated model for the TableAssociation table."""

    __tablename__ = "TableAssociation"

    association_id: Mapped[int] = mapped_column("AssociationID", primary_key=True)
    child_table_vid: Mapped[int] = mapped_column(
        "ChildTableVID",
        ForeignKey(TableVersion.table_vid),
    )
    parent_table_vid: Mapped[int] = mapped_column(
        "ParentTableVID",
        ForeignKey(TableVersion.table_vid),
    )
    name: Mapped[str] = mapped_column("Name")
    description: Mapped[str | None] = mapped_column("Description")
    is_identifying: Mapped[bool] = mapped_column("IsIdentifying")
    is_subtype: Mapped[bool] = mapped_column("IsSubtype")
    subtype_discriminator: Mapped[int | None] = mapped_column(
        "SubtypeDiscriminator",
        ForeignKey(Header.header_id),
    )
    parent_cardinality_and_optionality: Mapped[str] = mapped_column(
        "ParentCardinalityAndOptionality",
    )
    child_cardinality_and_optionality: Mapped[str] = mapped_column(
        "ChildCardinalityAndOptionality",
    )
    row_guid: Mapped[str] = mapped_column("RowGUID", ForeignKey(Concept.concept_guid))

    child_table_version: Mapped[TableVersion] = relationship(
        foreign_keys=child_table_vid,
    )
    parent_table_version: Mapped[TableVersion] = relationship(
        foreign_keys=parent_table_vid,
    )
    subtype_discriminator_header: Mapped[Header | None] = relationship(
        foreign_keys=subtype_discriminator,
    )
    unique_concept: Mapped[Concept] = relationship(foreign_keys=row_guid)


class TableLock(DPM):
    """Auto-generated model for the TableLock table."""

    __tablename__ = "TableLock"

    table_lock_id: Mapped[int] = mapped_column("TableLockID", primary_key=True)
    table_vid: Mapped[int] = mapped_column(
        "TableVID",
        ForeignKey(TableVersion.table_vid),
    )
    user_email: Mapped[str] = mapped_column("UserEmail")

    table_version: Mapped[TableVersion] = relationship(foreign_keys=table_vid)


class KeyHeaderMapping(DPM):
    """Auto-generated model for the KeyHeaderMapping table."""

    __tablename__ = "KeyHeaderMapping"

    association_id: Mapped[int] = mapped_column(
        "AssociationID",
        ForeignKey(TableAssociation.association_id),
        primary_key=True,
    )
    foreign_key_header_id: Mapped[int] = mapped_column(
        "ForeignKeyHeaderID",
        ForeignKey(Header.header_id),
        primary_key=True,
    )
    primary_key_header_id: Mapped[int] = mapped_column(
        "PrimaryKeyHeaderID",
        ForeignKey(Header.header_id),
    )
    row_guid: Mapped[str] = mapped_column("RowGUID", ForeignKey(Concept.concept_guid))

    association: Mapped[TableAssociation] = relationship(foreign_keys=association_id)
    foreign_key_header: Mapped[Header] = relationship(
        foreign_keys=foreign_key_header_id,
    )
    primary_key_header: Mapped[Header] = relationship(
        foreign_keys=primary_key_header_id,
    )
    unique_concept: Mapped[Concept] = relationship(foreign_keys=row_guid)


class OperandReferenceLocation(DPM):
    """Auto-generated model for the OperandReferenceLocation table."""

    __tablename__ = "OperandReferenceLocation"

    operand_reference_id: Mapped[int] = mapped_column(
        "OperandReferenceID",
        ForeignKey(OperandReference.operand_reference_id),
        primary_key=True,
    )
    cell_id: Mapped[int] = mapped_column("CellID", ForeignKey(Cell.cell_id))
    table: Mapped[str] = mapped_column("Table")
    row: Mapped[str | None] = mapped_column("Row")
    column: Mapped[str] = mapped_column("Column")
    sheet: Mapped[str | None] = mapped_column("Sheet")

    operand_reference: Mapped[OperandReference] = relationship(
        foreign_keys=operand_reference_id,
    )
    cell: Mapped[Cell] = relationship(foreign_keys=cell_id)


class SubCategoryItem(DPM):
    """Auto-generated model for the SubCategoryItem table."""

    __tablename__ = "SubCategoryItem"

    item_id: Mapped[int] = mapped_column(
        "ItemID",
        ForeignKey(Item.item_id),
        primary_key=True,
    )
    sub_category_vid: Mapped[int] = mapped_column(
        "SubCategoryVID",
        ForeignKey(SubCategoryVersion.sub_category_vid),
        primary_key=True,
    )
    order: Mapped[int | None] = mapped_column("Order")
    label: Mapped[str | None] = mapped_column("Label")
    parent_item_id: Mapped[int | None] = mapped_column(
        "ParentItemID",
        ForeignKey(Item.item_id),
    )
    comparison_operator_id: Mapped[int | None] = mapped_column(
        "ComparisonOperatorID",
        ForeignKey(Operator.operator_id),
    )
    arithmetic_operator_id: Mapped[int | None] = mapped_column(
        "ArithmeticOperatorID",
        ForeignKey(Operator.operator_id),
    )
    row_guid: Mapped[str | None] = mapped_column(
        "RowGUID",
        ForeignKey(Concept.concept_guid),
    )

    parent_item: Mapped[Item | None] = relationship(foreign_keys=parent_item_id)
    comparison_operator: Mapped[Operator | None] = relationship(
        foreign_keys=comparison_operator_id,
    )
    arithmetic_operator: Mapped[Operator | None] = relationship(
        foreign_keys=arithmetic_operator_id,
    )
    unique_concept: Mapped[Concept | None] = relationship(foreign_keys=row_guid)
    item: Mapped[Item] = relationship(foreign_keys=item_id)
    sub_category_version: Mapped[SubCategoryVersion] = relationship(
        foreign_keys=sub_category_vid,
    )


class VariableVersion(DPM):
    """Auto-generated model for the VariableVersion table."""

    __tablename__ = "VariableVersion"

    variable_vid: Mapped[int] = mapped_column("VariableVID", primary_key=True)
    variable_id: Mapped[int] = mapped_column(
        "VariableID",
        ForeignKey(Variable.variable_id),
    )
    property_id: Mapped[int] = mapped_column(
        "PropertyID",
        ForeignKey(Property.property_id),
    )
    sub_category_vid: Mapped[int | None] = mapped_column(
        "SubCategoryVID",
        ForeignKey(SubCategoryVersion.sub_category_vid),
    )
    context_id: Mapped[int | None] = mapped_column(
        "ContextID",
        ForeignKey(Context.context_id),
    )
    key_id: Mapped[int | None] = mapped_column("KeyID", ForeignKey(CompoundKey.key_id))
    is_multi_valued: Mapped[bool] = mapped_column("IsMultiValued")
    code: Mapped[str | None] = mapped_column("Code")
    name: Mapped[str | None] = mapped_column("Name")
    start_release_id: Mapped[int] = mapped_column(
        "StartReleaseID",
        ForeignKey(Release.release_id),
    )
    end_release_id: Mapped[int | None] = mapped_column(
        "EndReleaseID",
        ForeignKey(Release.release_id),
    )
    row_guid: Mapped[str | None] = mapped_column(
        "RowGUID",
        ForeignKey(Concept.concept_guid),
    )

    key: Mapped[CompoundKey | None] = relationship(foreign_keys=key_id)
    start_release: Mapped[Release] = relationship(foreign_keys=start_release_id)
    end_release: Mapped[Release | None] = relationship(foreign_keys=end_release_id)
    unique_concept: Mapped[Concept | None] = relationship(foreign_keys=row_guid)
    variable: Mapped[Variable] = relationship(foreign_keys=variable_id)
    property: Mapped[Property] = relationship(foreign_keys=property_id)
    sub_category_version: Mapped[SubCategoryVersion | None] = relationship(
        foreign_keys=sub_category_vid,
    )
    context: Mapped[Context | None] = relationship(foreign_keys=context_id)


class HeaderVersion(DPM):
    """Auto-generated model for the HeaderVersion table."""

    __tablename__ = "HeaderVersion"

    header_vid: Mapped[int] = mapped_column("HeaderVID", primary_key=True)
    header_id: Mapped[int] = mapped_column("HeaderID", ForeignKey(Header.header_id))
    code: Mapped[str] = mapped_column("Code")
    label: Mapped[str] = mapped_column("Label")
    property_id: Mapped[int | None] = mapped_column(
        "PropertyID",
        ForeignKey(Property.property_id),
    )
    context_id: Mapped[int | None] = mapped_column(
        "ContextID",
        ForeignKey(Context.context_id),
    )
    sub_category_vid: Mapped[int | None] = mapped_column(
        "SubCategoryVID",
        ForeignKey(SubCategoryVersion.sub_category_vid),
    )
    key_variable_vid: Mapped[int | None] = mapped_column(
        "KeyVariableVID",
        ForeignKey(VariableVersion.variable_vid),
    )
    start_release_id: Mapped[int] = mapped_column(
        "StartReleaseID",
        ForeignKey(Release.release_id),
    )
    end_release_id: Mapped[int | None] = mapped_column(
        "EndReleaseID",
        ForeignKey(Release.release_id),
    )
    row_guid: Mapped[str] = mapped_column("RowGUID", ForeignKey(Concept.concept_guid))

    key_variable_version: Mapped[VariableVersion | None] = relationship(
        foreign_keys=key_variable_vid,
    )
    start_release: Mapped[Release] = relationship(foreign_keys=start_release_id)
    end_release: Mapped[Release | None] = relationship(foreign_keys=end_release_id)
    unique_concept: Mapped[Concept] = relationship(foreign_keys=row_guid)
    header: Mapped[Header] = relationship(foreign_keys=header_id)
    property: Mapped[Property | None] = relationship(foreign_keys=property_id)
    context: Mapped[Context | None] = relationship(foreign_keys=context_id)
    sub_category_version: Mapped[SubCategoryVersion | None] = relationship(
        foreign_keys=sub_category_vid,
    )


class KeyComposition(DPM):
    """Auto-generated model for the KeyComposition table."""

    __tablename__ = "KeyComposition"

    key_id: Mapped[int] = mapped_column(
        "KeyID",
        ForeignKey(CompoundKey.key_id),
        primary_key=True,
    )
    variable_vid: Mapped[int] = mapped_column(
        "VariableVID",
        ForeignKey(VariableVersion.variable_vid),
        primary_key=True,
    )
    row_guid: Mapped[str | None] = mapped_column(
        "RowGUID",
        ForeignKey(Concept.concept_guid),
    )

    key: Mapped[CompoundKey] = relationship(foreign_keys=key_id)
    unique_concept: Mapped[Concept | None] = relationship(foreign_keys=row_guid)
    variable_version: Mapped[VariableVersion] = relationship(foreign_keys=variable_vid)


class ModuleParameters(DPM):
    """Auto-generated model for the ModuleParameters table."""

    __tablename__ = "ModuleParameters"

    module_vid: Mapped[int] = mapped_column(
        "ModuleVID",
        ForeignKey(ModuleVersion.module_vid),
        primary_key=True,
    )
    variable_vid: Mapped[int] = mapped_column(
        "VariableVID",
        ForeignKey(VariableVersion.variable_vid),
        primary_key=True,
    )
    row_guid: Mapped[str | None] = mapped_column(
        "RowGUID",
        ForeignKey(Concept.concept_guid),
    )

    unique_concept: Mapped[Concept | None] = relationship(foreign_keys=row_guid)
    module_version: Mapped[ModuleVersion] = relationship(foreign_keys=module_vid)
    variable_version: Mapped[VariableVersion] = relationship(foreign_keys=variable_vid)


class TableVersionCell(DPM):
    """Auto-generated model for the TableVersionCell table."""

    __tablename__ = "TableVersionCell"

    table_vid: Mapped[int] = mapped_column(
        "TableVID",
        ForeignKey(TableVersion.table_vid),
        primary_key=True,
    )
    cell_id: Mapped[int] = mapped_column(
        "CellID",
        ForeignKey(Cell.cell_id),
        primary_key=True,
    )
    cell_code: Mapped[str] = mapped_column("CellCode")
    is_nullable: Mapped[bool] = mapped_column("IsNullable")
    is_excluded: Mapped[bool] = mapped_column("IsExcluded")
    is_void: Mapped[bool] = mapped_column("IsVoid")
    sign: Mapped[str | None] = mapped_column("Sign")
    variable_vid: Mapped[int | None] = mapped_column(
        "VariableVID",
        ForeignKey(VariableVersion.variable_vid),
    )
    row_guid: Mapped[str] = mapped_column("RowGUID", ForeignKey(Concept.concept_guid))

    unique_concept: Mapped[Concept] = relationship(foreign_keys=row_guid)
    table_version: Mapped[TableVersion] = relationship(foreign_keys=table_vid)
    cell: Mapped[Cell] = relationship(foreign_keys=cell_id)
    variable_version: Mapped[VariableVersion | None] = relationship(
        foreign_keys=variable_vid,
    )


class TableVersionHeader(DPM):
    """Auto-generated model for the TableVersionHeader table."""

    __tablename__ = "TableVersionHeader"

    table_vid: Mapped[int] = mapped_column(
        "TableVID",
        ForeignKey(TableVersion.table_vid),
        primary_key=True,
    )
    header_id: Mapped[int] = mapped_column(
        "HeaderID",
        ForeignKey(Header.header_id),
        primary_key=True,
    )
    header_vid: Mapped[int] = mapped_column(
        "HeaderVID",
        ForeignKey(HeaderVersion.header_vid),
    )
    parent_header_id: Mapped[int | None] = mapped_column(
        "ParentHeaderID",
        ForeignKey(Header.header_id),
    )
    parent_first: Mapped[bool] = mapped_column("ParentFirst")
    order: Mapped[int] = mapped_column("Order")
    is_abstract: Mapped[bool] = mapped_column("IsAbstract")
    is_unique: Mapped[bool] = mapped_column("IsUnique")
    row_guid: Mapped[str] = mapped_column("RowGUID", ForeignKey(Concept.concept_guid))

    parent_header: Mapped[Header | None] = relationship(foreign_keys=parent_header_id)
    unique_concept: Mapped[Concept] = relationship(foreign_keys=row_guid)
    table_version: Mapped[TableVersion] = relationship(foreign_keys=table_vid)
    header: Mapped[Header] = relationship(foreign_keys=header_id)
    header_version: Mapped[HeaderVersion] = relationship(foreign_keys=header_vid)
