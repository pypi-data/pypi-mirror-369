import logging
import uuid

import pytest
import geojson
import uuid
from terrascope.sdk.terrascope_sdk import TerraScopeSDK
from terrascope.sdk.tools.io import H3Tools


class TestIO:
    @pytest.mark.asyncio
    async def test_point_to_h3_boundary(self):
        h3_tools = H3Tools()
        filepath = "../resources/aois/geojson/attributed_sea_ports.geojson"
        sea_port_h3_geojson = h3_tools.points_to_h3_geometry(filename=filepath, resolution=10,
                                                             output="../resources/aois/geojson/sea_ports.geojson")
        # Need a better test here.
        assert sea_port_h3_geojson is not None

        # verify upload works
        sdk = TerraScopeSDK()
        aoi_collection_id = await sdk.aoi_collection.create(str(uuid.uuid4()))

        await sdk.aoi.upload(aoi_collection_id=aoi_collection_id,
                             file_path="../resources/aois/geojson/sea_ports.geojson")

        logging.info(sea_port_h3_geojson)
