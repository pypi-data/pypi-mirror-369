import logging
import uuid
from typing import List

import pytest

from terrascope.sdk.api.aoi import AOIInputBuilder
from terrascope.sdk.terrascope_sdk import TerraScopeSDK


class TestAOI:

    @pytest.mark.asyncio
    async def test_upload(self):

        sdk = TerraScopeSDK()
        aoi_collection = await sdk.aoi_collection.create(aoi_collection_name=str(uuid.uuid4()))

        assert aoi_collection.id is not None

        transaction = await sdk.aoi.upload(aoi_collection_id=aoi_collection.id,
                                           file_path="../resources/aois/geojson/us-amz-distro-centers.geojson")

        logging.info(transaction)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("name, category, category_type, tags", [
        ("test_name-{}".format(uuid.uuid4()), "industrial", "manufacturing", ["aoi_tag1", "aoi_tag2"]),
        ("1-test_name-{}".format(uuid.uuid4()), "residential", "apartments", ["aoi_tag1", "aoi_tag2"])])
    async def test_create(self,
                          name: str,
                          category: str,
                          category_type: str,
                          tags: List):
        sdk = TerraScopeSDK()

        aoi_collection = await sdk.aoi_collection.create(aoi_collection_name=name)

        assert aoi_collection.id is not None

        wkt = """POLYGON ((-121.891336 37.345116, -121.882978 37.322622, -121.865618 37.335404, -121.891336 37.345116))
        """
        aoi_builder = AOIInputBuilder()
        aoi = aoi_builder.build(geom_wkt=wkt,
                                name="aoi-" + name,
                                category=category,
                                type=category_type,
                                tags=['sdk-integration'],
                                # attributes={"organization": "google", "city": "Palo Alto"}
                                )
        aoi_identifiers = await sdk.aoi.create(aoi_collection_id=aoi_collection.id,
                                               aoi_inputs=[aoi])

        assert aoi_identifiers is not None

    @pytest.mark.asyncio
    @pytest.mark.parametrize("name, category, category_type, tags", [
        ("test_name-{}".format(uuid.uuid4()), "industrial", "manufacturing", ["aoi_tag1", "aoi_tag2"]),
        ("1-test_name-{}".format(uuid.uuid4()), "residential", "apartments", ["aoi_tag1", "aoi_tag2"])])
    async def test_get(self,
                       name: str,
                       category: str,
                       category_type: str,
                       tags: List):
        sdk = TerraScopeSDK()

        aoi_collection = await sdk.aoi_collection.create(aoi_collection_name=name)

        assert aoi_collection.id is not None

        wkt = """POLYGON ((-121.891336 37.345116, -121.882978 37.322622, -121.865618 37.335404, -121.891336 37.345116))
                """

        aoi_builder = AOIInputBuilder()
        aoi = aoi_builder.build(geom_wkt=wkt,
                                name="aoi-" + name,
                                category=category,
                                type=category_type,
                                tags=['sdk-integration'])
        aoi_identifiers = await sdk.aoi.create(aoi_collection_id=aoi_collection.id,
                                               aoi_inputs=[aoi])

        response = sdk.aoi.get(ids=aoi_identifiers, verbose=True)

        assert response is not None


class TestAOIVersion:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("name, category, category_type, tags", [
        ("test_name-{}".format(uuid.uuid4()), "industrial", "manufacturing", ["aoi_tag1", "aoi_tag2"]),
        ("1-test_name-{}".format(uuid.uuid4()), "residential", "apartments", ["aoi_tag1", "aoi_tag2"])])
    async def test_create(self,
                          name: str,
                          category: str,
                          category_type: str,
                          tags: List):
        sdk = TerraScopeSDK()

        aoi_collection = await sdk.aoi_collection.create(aoi_collection_name=name)

        assert aoi_collection.id is not None

        wkt = """POLYGON ((-121.891336 37.345116, -121.882978 37.322622, -121.865618 37.335404, -121.891336 37.345116))
        """
        aoi_builder = AOIInputBuilder()
        aoi = aoi_builder.build(geom_wkt=wkt,
                                name="aoi-" + name,
                                category=category,
                                type=category_type,
                                tags=['sdk-integration'],
                                # attributes={"organization": "google", "city": "Palo Alto"}
                                )
        aoi_identifiers = await sdk.aoi.create(aoi_collection_id=aoi_collection.id,
                                               aoi_inputs=[aoi])

        assert aoi_identifiers is not None

        aoi_version_id = sdk.aoi_version.create(aoi_identifiers[0], aoi_modification_input=aoi)

        assert aoi_version_id is not None

    @pytest.mark.asyncio
    async def test_get(self):
        print("test needs to be written")
        pass

    @pytest.mark.asyncio
    async def test_list(self):
        print("test needs to be written")
        pass


class TestAOICollection:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("name", [("test_name-{}".format(uuid.uuid4())),
                                      ("1-test_name-{}".format(uuid.uuid4()))])
    async def test_create(self, name):
        sdk = TerraScopeSDK()

        aoi_collection = await sdk.aoi_collection.create(aoi_collection_name=name)

        assert aoi_collection.id is not None


    @pytest.mark.asyncio
    async def test_get(self):
        sdk = TerraScopeSDK()

        aoi_collection = await sdk.aoi_collection.create(aoi_collection_name=str(uuid.uuid4()))

        assert aoi_collection.id is not None

        await sdk.aoi.upload(aoi_collection_id=aoi_collection.id,
                             file_path="../resources/aois/geojson/us-amz-distro-centers.geojson")

        aoi_collection = await sdk.aoi_collection.get(aoi_collection_id=aoi_collection.id)
        print(aoi_collection)


