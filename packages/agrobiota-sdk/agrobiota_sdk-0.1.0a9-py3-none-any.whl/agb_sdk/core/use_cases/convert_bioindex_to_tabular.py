from pathlib import Path
from typing import Any

from pandas import DataFrame, ExcelWriter

from agb_sdk.core.dtos.biotrop_bioindex import BiotropBioindex


async def convert_bioindex_to_tabular(
    bioindex: BiotropBioindex,
    output_path: Path | None = None,
    resolve_taxonomies: bool = True,
    **kwargs,
) -> tuple[DataFrame, DataFrame, DataFrame, DataFrame, DataFrame, DataFrame] | None:
    """Convert a BiotropBioindex to a Pandas DataFrame"""

    by_sample_data: list[dict[str, Any]] = []
    by_dimension_data: list[dict[str, Any]] = []
    by_process_data: list[dict[str, Any]] = []
    diversity_data: list[dict[str, Any]] = []
    community_composition_data: list[dict[str, Any]] = []

    # --------------------------------------------------------------------------
    # 0. Resolve taxonomies
    # --------------------------------------------------------------------------

    if resolve_taxonomies:
        bioindex = await bioindex.resolve_taxonomies(**kwargs)

    # --------------------------------------------------------------------------
    # 1. Summary data
    # --------------------------------------------------------------------------

    frame = DataFrame.from_records(
        [
            {
                "id": bioindex.id,
                "hash": bioindex.hash,
                "version": bioindex.version,
                "updated_at": bioindex.updated_at,
            }
        ],
    ).transpose()

    frame.columns = ["info"]

    # --------------------------------------------------------------------------
    # 2. By sample data
    # --------------------------------------------------------------------------

    for result in bioindex.results:
        by_sample_data.append(
            {
                "sample": result.sample,
                "ggh": result.ggh,
            }
        )

    by_sample_data_frame = DataFrame.from_records(by_sample_data)

    # --------------------------------------------------------------------------
    # 3. By dimension data
    # --------------------------------------------------------------------------

    for result in bioindex.results:
        by_dimension_data.extend(
            [
                {
                    "sample": result.sample,
                    "dimension": "biodiversity",
                    "ggh": result.by_dimension.biodiversity.ggh,
                },
                {
                    "sample": result.sample,
                    "dimension": "biological_agents",
                    "ggh": result.by_dimension.biological_agents.ggh,
                },
                {
                    "sample": result.sample,
                    "dimension": "biological_fertility",
                    "ggh": result.by_dimension.biological_fertility.ggh,
                },
                {
                    "sample": result.sample,
                    "dimension": "phytosanitary_risk",
                    "ggh": result.by_dimension.phytosanitary_risk.ggh,
                },
            ]
        )

    by_dimension_data_frame = DataFrame.from_records(by_dimension_data)

    # --------------------------------------------------------------------------
    # 4. By process data
    # --------------------------------------------------------------------------

    for result in bioindex.results:
        for process in result.by_dimension.biodiversity.by_process:
            by_process_data.append(
                {
                    "sample": result.sample,
                    "dimension": "biodiversity",
                    "process": process.process,
                    "ggh": process.ggh,
                }
            )

        for process in result.by_dimension.biological_agents.by_process:
            by_process_data.append(
                {
                    "sample": result.sample,
                    "dimension": "biological_agents",
                    "process": process.process,
                    "ggh": process.ggh,
                }
            )

        for process in result.by_dimension.biological_fertility.by_process:
            by_process_data.append(
                {
                    "sample": result.sample,
                    "dimension": "biological_fertility",
                    "group": process.group,
                    "process": process.process,
                    "ggh": process.ggh,
                }
            )

        for process in result.by_dimension.phytosanitary_risk.by_process:
            by_process_data.append(
                {
                    "sample": result.sample,
                    "dimension": "phytosanitary_risk",
                    "process": process.process,
                    "ggh": process.ggh,
                }
            )

    by_process_data_frame = DataFrame.from_records(by_process_data)

    # --------------------------------------------------------------------------
    # 5. Diversity data
    # --------------------------------------------------------------------------

    for result in bioindex.results:
        diversity_data.extend(
            [
                {
                    "sample": result.sample,
                    "taxon": "bacteria",
                    "faith_pd": result.diversity.statistics.faith_pd.bacteria.value,
                    "shannon": result.diversity.statistics.shannon.bacteria.value,
                    "richness": result.diversity.statistics.richness.bacteria.value,
                    "faith_pd_inverse_confidence": result.diversity.statistics.faith_pd.bacteria.inverse_confidence,
                    "shannon_inverse_confidence": result.diversity.statistics.shannon.bacteria.inverse_confidence,
                    "richness_inverse_confidence": result.diversity.statistics.richness.bacteria.inverse_confidence,
                },
                {
                    "sample": result.sample,
                    "taxon": "fungi",
                    "faith_pd": result.diversity.statistics.faith_pd.fungi.value,
                    "shannon": result.diversity.statistics.shannon.fungi.value,
                    "richness": result.diversity.statistics.richness.fungi.value,
                    "faith_pd_inverse_confidence": result.diversity.statistics.faith_pd.fungi.inverse_confidence,
                    "shannon_inverse_confidence": result.diversity.statistics.shannon.fungi.inverse_confidence,
                    "richness_inverse_confidence": result.diversity.statistics.richness.fungi.inverse_confidence,
                },
            ]
        )

    diversity_data_frame = DataFrame.from_records(diversity_data)

    # --------------------------------------------------------------------------
    # 6. Community composition data
    # --------------------------------------------------------------------------

    for result in bioindex.results:
        for taxon in result.diversity.community_composition:
            community_composition_data.extend(
                [
                    {
                        "sample": result.sample,
                        "taxon": taxon.taxon,
                        "taxon_id": taxon.key,
                        "count": taxon.count,
                        "is_pathogenic": taxon.is_pathogenic,
                    }
                ]
            )

    community_composition_data_frame = DataFrame.from_records(
        community_composition_data,
    )

    # --------------------------------------------------------------------------
    # 7. Persist as XLSX separated by tabs
    # --------------------------------------------------------------------------

    if output_path is not None and isinstance(output_path, Path):
        if not output_path.parent.exists():
            output_path.parent.mkdir(parents=True)

        output_path = output_path.with_suffix(".xlsx")

        with ExcelWriter(output_path, mode="w") as writer:
            frame.to_excel(writer, sheet_name="summary")
            by_sample_data_frame.to_excel(writer, sheet_name="by_sample")
            by_dimension_data_frame.to_excel(writer, sheet_name="by_dimension")
            by_process_data_frame.to_excel(writer, sheet_name="by_process")
            diversity_data_frame.to_excel(writer, sheet_name="diversity")
            community_composition_data_frame.to_excel(
                writer, sheet_name="community_composition"
            )

        return None

    # --------------------------------------------------------------------------
    # 8. Return the dataframes
    # --------------------------------------------------------------------------

    return (
        frame,
        by_sample_data_frame,
        by_dimension_data_frame,
        by_process_data_frame,
        diversity_data_frame,
        community_composition_data_frame,
    )
