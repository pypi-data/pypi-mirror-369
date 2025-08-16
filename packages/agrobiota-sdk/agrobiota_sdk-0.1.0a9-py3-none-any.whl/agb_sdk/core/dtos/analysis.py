from typing import Any, List, Optional, Self, Union

from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class CustomerRecord(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    id: str
    short_name: str
    full_name: Optional[Any] = None
    description: Optional[Any] = None
    results_set: Optional[Any] = None


class Customer(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    record: CustomerRecord


class CustomerId(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    id: str


class ParentId(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    id: str


class BioindexIds(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    ids: List[str]


class Tag(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    id: str
    value: str
    meta: Any


class ResultSet(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    id: str


class Artifact(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    id: str
    result_set: ResultSet
    name: str
    url: str
    artifact_type: str
    public_object: bool
    updated_at: str


class Group(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    # Empty interface in TypeScript, keeping as empty for now
    pass


class Sample(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    # Empty interface in TypeScript, keeping as empty for now
    pass


class Metadata(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    group: Group
    sample: Sample


class Analysis(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    customer: Union[Customer, CustomerId]
    id: str
    parent: Union[ParentId, Any]
    result_type: str
    name: str
    tags: Optional[List[Tag]] = None
    hash: str
    version: int
    updated_at: str
    collection_date: Optional[Any] = None
    crop: str
    taxa: str
    was_frozen: bool
    was_approved: bool
    was_evaluated: bool
    was_rejected: bool
    upload_completed: bool
    verbose_status: str
    artifacts: Optional[List[Artifact]] = None
    aggregation_set: Optional[Any] = None
    sample_statistics: Optional[Any] = None
    show_recommendation: bool
    children: Optional[List["Analysis"]] = None
    bioindex: Optional[BioindexIds] = None

    def list_bioindex_ids(self) -> List[str]:
        """List the bioindex IDs."""

        bioindex_ids: list[str] = []

        if self.bioindex:
            bioindex_ids.extend(self.bioindex.ids)

        if self.children:
            for child in self.children:
                bioindex_ids.extend(child.list_bioindex_ids())

        return bioindex_ids


class AnalysisList(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    count: int
    skip: int
    size: int
    records: List[Analysis]
