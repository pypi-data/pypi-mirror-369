from dataclasses import dataclass
from typing import Optional

from fastapi import Query
from titiler.core.dependencies import DefaultDependency


@dataclass
class STACAssetsParams(DefaultDependency):
    """Band names and Expression parameters."""

    assets: Optional[str] = Query(
        None,
        title="asset names",
        description="comma (',') delimited bands names.",
    )

    def __post_init__(self):
        """Post Init."""
        if self.assets is not None:
            #self.kwargs["assets"] = self.assets.split(",")
            self.assets = self.assets.split(",")
