from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel


class BiotaxResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    tax_id: int
    tax_name: str
    name_class: str
    rank: str
    division: str
    parent: int | None = None
    unique_name: str | None = None


class TaxonomyResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    tax_id: int
    tax_name: str
    name_class: str

    other_names: list[str]
