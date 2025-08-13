import pytest

from terrascope.sdk.terrascope_sdk import TerraScopeSDK


class TestDataSource:
    @pytest.mark.asyncio
    async def test_get(self):
        sdk = TerraScopeSDK()
        ids = ["blogwatcher_pings", "adsbx_pings"]
        sources = await sdk.data_source.get(ids=ids)
        assert len(sources) == len(ids)

    @pytest.mark.asyncio
    async def test_list(self):
        sdk = TerraScopeSDK()
        data_sources = await sdk.data_source.list()
        assert len(data_sources) > 0

        data_sources = await sdk.data_source.list(search_text="exact-earth")
        assert len(data_sources) == 2


class TestDataType:
    @pytest.mark.asyncio
    async def test_get(self):
        sdk = TerraScopeSDK()
        data_types = await sdk.data_type.get(ids=["pings"])
        assert len(data_types) == 1

    @pytest.mark.asyncio
    async def test_list(self):
        sdk = TerraScopeSDK()
        data_types = await sdk.data_type.list()
        assert len(data_types) > 0

        data_types = await sdk.data_type.list(search_text="ping")
        assert len(data_types) == 2

    @pytest.mark.asyncio
    async def test_create(self):
        sdk = TerraScopeSDK()
        data_type = await sdk.data_type.create(name="test_data_type", description="test description", schema="", data_source_ids=[])
