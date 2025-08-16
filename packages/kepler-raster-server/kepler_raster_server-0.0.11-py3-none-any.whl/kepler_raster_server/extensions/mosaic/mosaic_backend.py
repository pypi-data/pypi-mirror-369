from typing import Dict, List, Type
from urllib.parse import urlparse

import attr
import planetary_computer as pc
import pystac
from cogeo_mosaic.backends.base import BaseBackend
from cogeo_mosaic.mosaic import MosaicJSON
from rio_tiler.io import BaseReader, STACReader

from .utils import _fetch


@attr.s
class DynamicStacBackend(BaseBackend):
    """Dynamic STAC backend for cogeo-mosaic readers

    The main difference between cogeo_mosaic's native STACBackend and this
    DynamicStacBackend is that the former actually creates a MosaicJSON document
    internally. That adds overhead and is generally unnecessary.

    This is derived from the example here:
    https://developmentseed.org/cogeo-mosaic/examples/Create_a_Dynamic_StacBackend/
    """

    # Need to move `asset` one place to the right since the STACReader takes a URL as the first arg, and the STAC item itself as the second arg
    reader: Type[BaseReader] = attr.ib(
        default=lambda *args, **kwargs: STACReader(None, *args, **kwargs)
    )

    query: Dict = attr.ib(factory=dict)

    # STAC API related options
    # max_items |  next_link_key | limit
    stac_api_options: Dict = attr.ib(factory=dict)

    # The reader is read-only, we can't pass mosaic_def to the init method
    mosaic_def: MosaicJSON = attr.ib(init=False)

    minzoom: int = attr.ib(default=0)
    maxzoom: int = attr.ib(default=30)

    _backend_name = "DynamicSTAC"

    def __attrs_post_init__(self):
        """Post Init."""
        # Construct a FAKE mosaicJSON
        # mosaic_def has to be defined. 
        # we set `tiles` to an empty list.
        self.mosaic_def = MosaicJSON(
            mosaicjson="0.0.2",
            name="it's fake but it's ok",
            minzoom=self.minzoom,
            maxzoom=self.maxzoom,
            tiles=dict(), # []
        )

    def write(self, overwrite: bool = True):
        """This method is not used but is required by the abstract class."""
        pass

    def update(self):
        """We overwrite the default method."""
        pass

    def _read(self) -> MosaicJSON:
        """This method is not used but is required by the abstract class."""
        pass

    def assets_for_tile(self, x: int, y: int, z: int) -> List[str]:
        """Retrieve assets for tile."""
        bounds = self.tms.bounds(x, y, z)
        geom = {
            "type": "Polygon",
            "coordinates": [
                [
                    [bounds[0], bounds[3]],
                    [bounds[0], bounds[1]],
                    [bounds[2], bounds[1]],
                    [bounds[2], bounds[3]],
                    [bounds[0], bounds[3]],
                ]
            ],
        }
        return self.get_assets(geom)

    def assets_for_point(self, lng: float, lat: float) -> List[str]:
        """Retrieve assets for point."""
        EPSILON = 1e-14
        geom = {
            "type": "Polygon",
            "coordinates": [
                [
                    [lng - EPSILON, lat + EPSILON],
                    [lng - EPSILON, lat - EPSILON],
                    [lng + EPSILON, lat - EPSILON],
                    [lng + EPSILON, lat + EPSILON],
                    [lng - EPSILON, lat + EPSILON],
                ]
            ],
        }
        return self.get_assets(geom)

    def get_assets(self, geom) -> List[str]:
        """Find assets."""
        query = self.query.copy()
        query["intersects"] = geom

        path = self.input # self.path

        features = _fetch(
            path,
            query,
            **self.stac_api_options,
        )

        # If the STAC API is hosted on Microsoft's servers, assume it's
        # necessary to use the Planetary computer's signing mechanism
        if "microsoft.com" in urlparse(path).netloc:
            return [pc.sign_assets(pystac.Item.from_dict(f)) for f in features]

        return list(features)

    @property
    def _quadkeys(self) -> List[str]:
        return []
