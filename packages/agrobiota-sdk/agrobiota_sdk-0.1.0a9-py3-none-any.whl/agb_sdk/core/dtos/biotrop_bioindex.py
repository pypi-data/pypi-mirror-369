import logging
from asyncio import gather, sleep
from typing import Any, Self

from aiohttp import ClientSession
from aiohttp.client_exceptions import ClientError
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

from agb_sdk.core.dtos import BiotaxResponse, TaxonomyResponse
from agb_sdk.settings import DEFAULT_TAXONOMY_URL

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class ByProcess(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    process: str
    ggh: float


class ByProcessWithGroup(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    process: str
    ggh: float
    group: str | None = None


class Dimension(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    ggh: float
    by_process: list[ByProcess]


class BiologicalFertilityDimension(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    ggh: float
    by_process: list[ByProcessWithGroup]


class ByDimension(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    biodiversity: Dimension
    biological_agents: Dimension
    biological_fertility: BiologicalFertilityDimension
    phytosanitary_risk: Dimension


class CommunityComposition(BaseModel):
    """The community composition of the sample"""

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    key: str
    """The Tax ID of the taxon"""

    key_type: str
    """The type of the key. Current options include just `taxid`"""

    count: int
    """The occurrence count of the taxon at the sample"""

    is_pathogenic: bool
    """Whether the taxon is pathogenic"""

    taxon: str | None = None
    """The taxon name"""

    alternative_names: list[str] | None = None
    """The alternative names of the taxon"""


class TaxonStatistics(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    value: float
    inverse_confidence: float


class ByTaxonomy(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    fungi: TaxonStatistics | None = None
    bacteria: TaxonStatistics | None = None


class Statistics(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    faith_pd: ByTaxonomy
    shannon: ByTaxonomy
    richness: ByTaxonomy


class Diversity(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    statistics: Statistics
    community_composition: list[CommunityComposition]


class Result(BaseModel):
    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    sample: str
    ggh: float
    diversity: Diversity
    by_dimension: ByDimension


class BiotropBioindex(BaseModel):
    """The Biotrop Bioindex

    Using this class, you can deserialize the Biotrop Bioindex from the JSON
    response, derived from the Agrobiota Customer's API.
    """

    model_config = ConfigDict(populate_by_name=True, alias_generator=to_camel)

    id: str
    """The ID of the Biotrop Bioindex record"""

    hash: str
    """The Bioindex hash

    This hash is used to identify the source of the Biotrop Bioindex. Using this
    hash results, users can identify independent bioindex generated from the
    same results.
    """

    version: int
    """The version of the Biotrop Bioindex."""

    updated_at: str
    """The date and time when the Biotrop Bioindex was updated."""

    results: list[Result]
    """The results of the Biotrop Bioindex.

    Here resides the most important information about the Biotrop Bioindex: the
    functional annotation itself. Each result contains the biodiversity,
    biological agents, biological fertility, and phytosanitary risk dimensions.
    """

    # --------------------------------------------------------------------------
    # PRIVATE PROPERTIES
    # --------------------------------------------------------------------------

    @property
    def __default_taxonomy_url(self) -> str:
        """The URL to the taxonomy of the Biotrop Bioindex."""

        return DEFAULT_TAXONOMY_URL

    @property
    def __default_chunk_size(self) -> int:
        """The default chunk size for the Biotrop Bioindex."""

        return 25

    @property
    def __unique_taxonomies(self) -> list[str]:
        """The unique taxonomies of the Biotrop Bioindex."""

        return list(
            set(
                composition.key
                for result in self.results
                for composition in result.diversity.community_composition
            )
        )

    # --------------------------------------------------------------------------
    # PUBLIC INSTANCE METHODS
    # --------------------------------------------------------------------------

    async def resolve_taxonomies(
        self,
        **kwargs,
    ) -> Self:
        """Resolve the taxonomy of the Biotrop Bioindex."""

        chunks = self.__chunk_list(
            items=self.__unique_taxonomies,
            chunk_size=self.__default_chunk_size,
        )

        chunk_total = len(chunks)

        resolved_taxonomies: list[TaxonomyResponse | None] = []

        for index, chunk in enumerate(chunks):
            chunk_index = index + 1

            logger.info(f"Resolving taxonomy for chunk {chunk_index} of {chunk_total}")
            results = await self.__batch_resolve_taxonomy(chunk, **kwargs)
            logger.info(f"Resolved taxonomy for chunk {chunk_index} of {chunk_total}")

            if results is None:
                logger.error(
                    f"Failed to resolve taxonomy for chunk {chunk_index} of {chunk_total} with taxIds: {', '.join(chunk)}"
                )

                continue

            resolved_taxonomies.extend(results)

            await sleep(1)

        for result in self.results:
            for composition in result.diversity.community_composition:
                taxon = next(
                    (
                        taxon
                        for taxon in resolved_taxonomies
                        if str(taxon.tax_id) == composition.key
                    ),
                    None,
                )

                composition.taxon = taxon.tax_name
                composition.alternative_names = taxon.other_names

        return self

    # --------------------------------------------------------------------------
    # PRIVATE INSTANCE METHODS
    # --------------------------------------------------------------------------

    async def __batch_resolve_taxonomy(
        self,
        taxa: list[str],
        **kwargs,
    ) -> list[TaxonomyResponse | None]:
        """Resolve the taxonomy of the Biotrop Bioindex."""

        tasks = [self.__resolve_taxonomy(taxid, **kwargs) for taxid in taxa]
        return await gather(*tasks)

    async def __resolve_taxonomy(
        self,
        taxid: str,
        taxonomy_url: str | None = None,
    ) -> TaxonomyResponse | None:
        """Resolve a single taxonomy of the Biotrop Bioindex."""

        max_attempts = 5
        current_attempt = 0

        try:
            for attempt in range(max_attempts):
                current_attempt = attempt + 1

                if current_attempt > 1:
                    logger.warning(
                        f"Retrying to resolve taxonomy for {taxid} (attempt {current_attempt})"
                    )

                # Wait a bit before retrying
                await sleep(2**attempt)

                async with ClientSession() as session:
                    async with session.get(
                        f"{taxonomy_url or self.__default_taxonomy_url}/{taxid}",
                        timeout=120,
                    ) as response:
                        #
                        # For successful requests try to collect the taxon
                        # records and return a TaxonomyResponse object.
                        #
                        if response.status > 200 and response.status < 300:
                            content_type = response.headers.get("Content-Type")

                            raw_records = await response.json(content_type=content_type)

                            records: list[BiotaxResponse] = [
                                BiotaxResponse.model_validate(record)
                                for record in raw_records
                            ]

                            target_record = list(
                                filter(
                                    lambda record: record.name_class
                                    == "scientific name",
                                    records,
                                ),
                            )

                            if len(target_record) == 0:
                                logger.error(
                                    f"No scientific name found for {taxid} in {records}"
                                )

                                return None

                            target_record: BiotaxResponse = target_record.pop()

                            return TaxonomyResponse(
                                tax_id=target_record.tax_id,
                                tax_name=target_record.tax_name,
                                name_class=target_record.name_class,
                                other_names=[record.tax_name for record in records],
                            )

                        #
                        # If the request was not successful, wait a bit and try
                        # again. If the maximum number of attempts is reached,
                        # return None.
                        #
                        if attempt == max_attempts - 1:
                            logger.error(
                                f"Failed to resolve taxonomy for {taxid} after {max_attempts} attempts"
                            )

                            return None

                        await sleep(2**attempt)
                        continue

        except Exception as error:
            logger.error(f"Failed to resolve taxonomy for {taxid}: {error}")
            return None

    # --------------------------------------------------------------------------
    # PRIVATE STATIC METHODS
    # --------------------------------------------------------------------------

    @staticmethod
    def __chunk_list(
        items: list[Any],
        chunk_size: int,
    ) -> list[list[Any]]:
        """Chunk the list into smaller lists of the given size."""

        return [items[i : i + chunk_size] for i in range(0, len(items), chunk_size)]
