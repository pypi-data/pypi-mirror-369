from fastapi import FastAPI
from titiler.application.main import app

from rio_tiler.io import Reader, STACReader
from titiler.core.factory import TilerFactory
from titiler.core.resources.enums import OptionalHeader

from .extensions.terrain import terrainExtension
from .extensions.mosaic import (STACAssetsParams, DynamicStacBackend, STACMosaicTilerFactory)

###############################################################################
# Quantized terrain mesh
terrain = TilerFactory(
    reader=Reader,
    router_prefix="/mesh",
    extensions=[
        terrainExtension(max_size=64)
    ],
)

app.include_router(
    terrain.router,
    prefix="/mesh",
    tags=["Quantized terrain mesh"],
)

###############################################################################
# Mosaics using a STAC API
stac_mosaic_tiler = STACMosaicTilerFactory(
    router_prefix="/stac/mosaic",
    backend=DynamicStacBackend,
    dataset_reader=lambda *args, **kwargs: STACReader(None, *args, **kwargs),
    layer_dependency=STACAssetsParams,
    optional_headers=[OptionalHeader.server_timing],
)
app.include_router(
    stac_mosaic_tiler.router, prefix="/stac/mosaic", tags=["STAC Mosaics"]
)

# Export the app
__all__ = ["app"]