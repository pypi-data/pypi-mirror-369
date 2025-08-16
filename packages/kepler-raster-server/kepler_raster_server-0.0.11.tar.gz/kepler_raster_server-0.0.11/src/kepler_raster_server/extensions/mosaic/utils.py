"""cogeo-mosaic STAC backend."""

import json
from typing import Dict, List, Optional

import requests
from cachetools import TTLCache, cached
from cachetools.keys import hashkey
from cogeo_mosaic.backends.stac import query_from_link
from cogeo_mosaic.cache import cache_config
from cogeo_mosaic.errors import _HTTP_EXCEPTIONS, MosaicError
from cogeo_mosaic.logger import logger


@cached(
    TTLCache(maxsize=cache_config.maxsize, ttl=cache_config.ttl),
    key=lambda url, query, **kwargs: hashkey(url, json.dumps(query), **kwargs),
)
def _fetch(
    stac_url: str,
    query: Dict,
    max_items: Optional[int] = None,
    next_link_key: Optional[str] = None,
    limit: int = 500,
) -> List[Dict]:
    """Call STAC API.

    Copied from https://github.com/developmentseed/cogeo-mosaic/blob/53409dbf1f6858393f017c5a1db205e58cb44ee6/cogeo_mosaic/backends/stac.py#L135-L220

    Modified because these lines (https://github.com/developmentseed/cogeo-mosaic/blob/53409dbf1f6858393f017c5a1db205e58cb44ee6/cogeo_mosaic/backends/stac.py#L191-L192) fail when the returned result has neither a `meta` nor `context` key.
    """
    features: List[Dict] = []
    stac_query = query.copy()

    headers = {
        "Content-Type": "application/json",
        "Accept-Encoding": "gzip",
        "Accept": "application/geo+json",
    }

    if "limit" not in stac_query:
        stac_query.update({"limit": limit})

    def _stac_search(url: str, q: Dict):
        try:
            r = requests.post(url, headers=headers, json=q)
            r.raise_for_status()
        except requests.exceptions.HTTPError as e:
            # post-flight errors
            status_code = e.response.status_code

            # A status code of 404 on a STAC Search request often means that the server could not
            # find data that matches the request. In that case, we want to fail gracefully so that
            # we don't spam Sentry
            if status_code == 404:
                return {}

            exc = _HTTP_EXCEPTIONS.get(status_code, MosaicError)
            raise exc(e.response.content) from e
        except requests.exceptions.RequestException as e:
            # pre-flight errors
            raise MosaicError(e.args[0].reason) from e
        return r.json()

    page = 1
    while True:
        logger.debug(f"Fetching page {page}")
        logger.debug("query: " + json.dumps(stac_query))

        results = _stac_search(stac_url, stac_query)
        if not results.get("features"):
            break

        features.extend(results["features"])
        if max_items and len(features) >= max_items:
            features = features[:max_items]
            break

        # new STAC context spec
        # {"page": 1, "limit": 1000, "matched": 5671, "returned": 1000}
        # SAT-API META
        # {"page": 4, "limit": 100, "found": 350, "returned": 50}
        ctx = results.get("context", results.get("meta"))

        if not ctx:
            break

        matched = ctx.get("matched", ctx.get("found"))

        if not matched:
            break

        logger.debug(json.dumps(ctx))
        # Check if there is more data to fetch
        if matched <= ctx["returned"]:
            break

        # We shouldn't fetch more item than matched
        if len(features) == matched:
            break

        if len(features) > matched:
            raise MosaicError(
                "Something weird is going on, please open an issue in https://github.com/developmentseed/cogeo-mosaic"
            )
        page += 1

        # https://github.com/radiantearth/stac-api-spec/blob/master/api-spec.md#paging-extension
        if next_link_key:
            links = list(
                filter(lambda link: link["rel"] == next_link_key, results["links"])
            )
            if not links:
                break
            stac_query = query_from_link(links[0], stac_query)
        else:
            stac_query.update({"page": page})

    return features
