import logging
from urllib.parse import urlencode

from aiohttp import ClientSession

from agb_sdk.core.dtos import AnalysisList, BiotropBioindex
from agb_sdk.settings import DEFAULT_CONNECTION_STRING_HEADER, DEFAULT_CUSTOMERS_API_URL

logger = logging.getLogger(__name__)


async def list_analysis(
    connection_string: str,
    report_id: str | None = None,
    custom_api_url: str | None = None,
    term: str | None = None,
    skip: int | None = None,
    size: int | None = None,
    **_,
) -> tuple[AnalysisList | None, BiotropBioindex | None, int | None]:
    """List my analysis from Agroportal API"""

    url: str | None = None

    if report_id:
        url = f"{custom_api_url or DEFAULT_CUSTOMERS_API_URL}/analysis/bioindex/{report_id}"
    else:
        url = f"{custom_api_url or DEFAULT_CUSTOMERS_API_URL}/analysis"

    params = {}

    if term:
        params.update({"name": term})

    if skip:
        params.update({"skip": skip})

    if size:
        params.update({"size": size})

    if params:
        url = f"{url}?{urlencode(params)}"

    try:
        analysis_list: AnalysisList | None = None
        biotrop_bioindex: BiotropBioindex | None = None
        response_status: int | None = None

        async with ClientSession() as session:
            async with session.get(
                url,
                timeout=120,
                headers={
                    DEFAULT_CONNECTION_STRING_HEADER: connection_string,
                },
                params=params,
            ) as response:
                if response.status not in [200, 204]:
                    logger.error(f"Error listing analysis: {response.status}")

                content_type = response.headers.get("Content-Type")
                raw_records = await response.json(content_type=content_type)

                if report_id:
                    biotrop_bioindex = BiotropBioindex.model_validate(raw_records)
                else:
                    analysis_list = AnalysisList.model_validate(raw_records)

                response_status = response.status

        return analysis_list, biotrop_bioindex, response_status

    except Exception as e:
        logger.error(f"Error listing analysis: {e}")
        return None, None, 500
