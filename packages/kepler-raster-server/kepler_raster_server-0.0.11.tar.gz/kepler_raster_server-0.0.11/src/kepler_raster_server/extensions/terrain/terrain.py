from dataclasses import dataclass, field
from typing import Tuple, List, Literal, Optional
from typing_extensions import Annotated
from io import BytesIO

from morecantile import tms as morecantile_tms
from morecantile.defaults import TileMatrixSets

from quantized_mesh_encoder import encode as qme_encode
from quantized_mesh_encoder import Ellipsoid
from pymartini import Martini, rescale_positions as martini_rescale_positions
from pydelatin import Delatin
from pydelatin.util import rescale_positions as delatin_rescale_positions
from pydelatin.util import decode_ele

from attrs import define
import rasterio
from starlette.responses import Response
from fastapi import Depends, FastAPI, Path, Query
from titiler.core.factory import FactoryExtension, TilerFactory
from titiler.core.resources.enums import ImageType

from numpy import float32, transpose

def tile_to_mesh_martini(tile, bounds, tile_size: int = 512, max_error: float = 10.0, flip_y: bool = False):
    martini = Martini(tile_size) 
    tin = martini.create_tile(tile.astype(float32))
    vrt, tri = tin.get_mesh(max_error=max_error)
    res = martini_rescale_positions(vrt, tile, bounds=bounds, flip_y=flip_y)
    return res, tri


def tile_to_mesh_delatin(tile, bounds, tile_size: int = 512, max_error: float = 10.0, flip_y: bool = False):
    tin = Delatin(tile, height=tile_size, width=tile_size, max_error=max_error)
    vrt, tri = tin.vertices, tin.triangles.flatten()
    res = delatin_rescale_positions(vrt, bounds, flip_y=flip_y)
    return res, tri

from .terrain_responses import QMEResponse, qme_responses

from math import pi, tan, atan, sinh, degrees

def tile_bounds(z, x, y):
    n = 2 ** z

    lon_left = x / n * 360.0 - 180.0
    lon_right = (x + 1) / n * 360.0 - 180.0

    lat_top = degrees(atan(sinh(pi * (1 - 2 * y / n))))
    lat_bottom = degrees(atan(sinh(pi * (1 - 2 * (y + 1) / n))))

    return [lon_left, lat_bottom, lon_right, lat_top]

@define
class terrainExtension(FactoryExtension):
    """Add endpoint to a TilerFactory."""

    # TileMatrixSet dependency
    supported_tms: TileMatrixSets = morecantile_tms
    # Max elevation map size
    max_size: int = field(default=128)

    # Register method is mandatory and must take a BaseFactory object as input
    def register(self, factory: TilerFactory):
        """Register endpoint to the tiler factory."""
        @factory.router.get(r"/tiles/{z}/{x}/{y}.{format}", response_class=QMEResponse, responses=qme_responses)
        def terrain(
            z: int = Path(..., ge=0, le=15, description="TMS tiles's zoom level"),
            x: int = Path(..., description="TMS tiles's column"),
            y: int = Path(..., description="TMS tiles's row"),
            format: Optional[Literal['terrain']] = Path(description="Type of the item, default is 'terrain'"),
            # scale: Optional[int] = Path(gt=0, lt=4, description="Tile size scale. 1=256x256, 2=512x512..."),

            # custom params for terrain
            mesh_quantizer: Literal['martini', 'delatin'] = Query("delatin", description="Mesh encoding algorithm to use"),
            #buffer: Optional[float] = Query(
            #    None,
            #    gt=0,
            #    title="Tile buffer.",
            #    description="Buffer on each side of the given tile. It must be a multiple of `0.5`. Output **tilesize** will be expanded to `tilesize + 2 * buffer` (e.g 0.5 = 257x257, 1.0 = 258x258).",
            #),
            mesh_max_error: Optional[float] = Query(10, description="Mesh max error"),
            
            # we can reuse the factory dependency
            src_path: str = Depends(factory.path_dependency),
            layer_params=Depends(factory.layer_dependency),
            dataset_params=Depends(factory.dataset_dependency),
            post_process=Depends(factory.process_dependency),
            render_params=Depends(factory.render_dependency),
            reader_params=Depends(factory.reader_dependency),
            env=Depends(factory.environment_dependency)
        ):
            tms = self.supported_tms.get('WebMercatorQuad')

            elevation_url = f"https://s3.amazonaws.com/elevation-tiles-prod/terrarium/{z}/{x}/{y}.png"
            with rasterio.Env(**env):
                with factory.reader(elevation_url, tms=tms, **reader_params.as_dict()) as src_dst:
                    image = src_dst.read(
                            **layer_params.as_dict(),
                            **dataset_params.as_dict(),
                        )
            if post_process:
                image = post_process(image)
            #if rescale:
            #    image.rescale(rescale)

            # got the tile data, now do the work
            flip_y: bool = True 
            tile_size: int = image.data[0].shape[0] #this will be expanded by the buffer for martini
            bounds = tile_bounds(z, x, y) #

            dataToUse = image.data
            
            dataToUse = transpose(dataToUse, (1, 2, 0))

            dataToUse = decode_ele(dataToUse, 'terrarium')

            if mesh_quantizer == 'delatin':
                res, tri = tile_to_mesh_delatin(
                    dataToUse,
                    bounds,
                    tile_size=tile_size,
                    max_error=mesh_max_error,
                    flip_y=flip_y
                )
            else:
                res, tri = tile_to_mesh_martini(
                    dataToUse,
                    bounds,
                    tile_size=tile_size,
                    max_error=mesh_max_error,
                    flip_y=flip_y
                )

            # get the ellipsoid, todo cache
            #ellipsoid = Ellipsoid(tms.crs.ellipsoid.semi_major_metre, tms.crs.ellipsoid.semi_minor_metre)
            with BytesIO() as out:
                qme_encode(
                    out,
                    res,
                    tri,
                    bounds=bounds,
                    sphere_method='naive',
                    #ellipsoid=ellipsoid
                )
                out.seek(0)
                return Response(out.read(), media_type="application/vnd.quantized-mesh")
