from datetime import datetime

import pytest
from google.protobuf.timestamp_pb2 import Timestamp

from terrascope.sdk.builder.toi import TOIBuilder, TOIRuleBuilder, Frequency
from terrascope.sdk.terrascope_sdk import TerraScopeSDK


class TestToi:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("start, finish, frequency, interval", [
        ("2019-01-05 01:00:00", "2019-01-15 01:00:00", Frequency.DAILY, 1)])
    async def test_toi_create(self, start, finish, frequency, interval):
        sdk = TerraScopeSDK()
        datetime_format = '%Y-%m-%d %H:%M:%S'
        toi_configuration = TOIBuilder()
        toi_configuration.build_toi(start=datetime.strptime(start, datetime_format),
                                    finish=datetime.strptime(finish, datetime_format),
                                    description="basic_test_toi")

        toi_configuration.build_recurrence(TOIRuleBuilder.build_rule(frequency=frequency,
                                                                     interval=interval))

        toi = await sdk.toi.create(toi_configuration.get())
        assert toi.id is not None
        assert len(toi.recurrences) == 1

    @pytest.mark.asyncio
    @pytest.mark.parametrize("start, finish, frequency, interval", [
        ("2019-01-05 01:00:00", "2019-01-15 01:00:00", Frequency.DAILY, 1)])
    async def test_toi_get(self, start, finish, frequency, interval):
        sdk = TerraScopeSDK()
        datetime_format = '%Y-%m-%d %H:%M:%S'
        toi_configuration = TOIBuilder()
        toi_configuration.build_toi(start=datetime.strptime(start, datetime_format),
                                    finish=datetime.strptime(finish, datetime_format),
                                    description="basic_test_toi")

        toi_configuration.build_recurrence(TOIRuleBuilder.build_rule(frequency=frequency,
                                                                     interval=interval))

        toi = await sdk.toi.create(toi_configuration.get())
        assert toi.id is not None
        assert len(toi.recurrences) == 1

        tois = await sdk.toi.get([toi.id])
        assert tois is not None

    @pytest.mark.asyncio
    @pytest.mark.parametrize("start, finish, frequency, interval, count", [
        ("2019-01-05 01:00:00", "2019-01-15 01:00:00", Frequency.DAILY, 1, 10),
        ("2019-01-05 01:00:00", "2019-01-15 01:00:00", Frequency.DAILY, 2, 3),
        ("2019-01-05 01:00:00", "2019-02-01 01:00:00", Frequency.WEEKLY, 1, 1),
        ("2019-01-05 01:00:00", "2019-06-01 01:00:00", Frequency.MONTHLY, 1, 3)])
    async def test_toi_create_get_occurrence(self, start, finish, frequency, interval, count):
        sdk = TerraScopeSDK()
        datetime_format = '%Y-%m-%d %H:%M:%S'
        toi_configuration = TOIBuilder()
        toi_configuration.build_toi(start=datetime.strptime(start, datetime_format),
                                    finish=datetime.strptime(finish, datetime_format),
                                    description="toi test occurrence {}".format(count))

        toi_configuration.build_recurrence(TOIRuleBuilder.build_rule(frequency=frequency,
                                                                     interval=interval,
                                                                     count=count))
        toi = await sdk.toi.create(toi_configuration.get())

        assert toi.id is not None
        assert len(toi.recurrences) == 1
        tois = await sdk.toi.get([toi.id])

        assert tois is not None
        for toi in tois:
            assert toi.recurrences[0].rule == "FREQ={};INTERVAL={};COUNT={}".format(Frequency(frequency).name, interval,
                                                                                    count)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("start, finish, frequency, interval, until", [
        ("2019-01-05 01:00:00", "2019-01-15 01:00:00", Frequency.DAILY, 1, "20190130T010000Z"),
        ("2019-01-05 01:00:00", "2019-01-15 01:00:00", Frequency.DAILY, 2, "20190130T010000Z"),
        ("2019-01-05 01:00:00", "2019-02-01 01:00:00", Frequency.WEEKLY, 1, "20190330T010000Z"),
        ("2019-01-05 01:00:00", "2019-06-01 01:00:00", Frequency.MONTHLY, 1, "20190630T010000Z")])
    async def test_toi_create_get_until(self, start, finish, frequency, interval, until):
        sdk = TerraScopeSDK()
        datetime_format = '%Y-%m-%d %H:%M:%S'
        toi_configuration = TOIBuilder()
        toi_configuration.build_toi(start=datetime.strptime(start, datetime_format),
                                    finish=datetime.strptime(finish, datetime_format),
                                    description="toi test until {}".format(until))

        toi_configuration.build_recurrence(TOIRuleBuilder.build_rule(frequency=frequency,
                                                                     interval=interval,
                                                                     until=until))
        toi = await sdk.toi.create(toi_configuration.get())

        assert toi.id is not None
        assert len(toi.recurrences) == 1
        tois = await sdk.toi.get([toi.id])

        assert tois is not None
        for toi in tois:
            assert toi.recurrences[0].rule == "FREQ={};INTERVAL={};UNTIL={}".format(Frequency(frequency).name, interval,
                                                                                    until)

    @pytest.mark.asyncio
    @pytest.mark.parametrize("start, finish, frequencies, interval", [
        ("2019-01-05 01:00:00", "2019-01-15 01:00:00", [Frequency.DAILY, Frequency.WEEKLY], 1)])
    async def test_toi_multiple_recurrence(self, start, finish, frequencies, interval):
        sdk = TerraScopeSDK()
        datetime_format = '%Y-%m-%d %H:%M:%S'
        toi_configuration = TOIBuilder()
        toi_configuration.build_toi(start=datetime.strptime(start, datetime_format),
                                    finish=datetime.strptime(finish, datetime_format),
                                    description="toi test multiple recurrence")

        for frequency in frequencies:
            toi_configuration.build_recurrence(TOIRuleBuilder.build_rule(frequency=frequency,
                                                                         interval=interval))
        toi = await sdk.toi.create(toi_configuration.get())

        assert toi.id is not None
        assert len(toi.recurrences) == 2
        tois = await sdk.toi.get([toi.id])

        assert tois is not None
        assert len(toi.recurrences) == 2


class TestToiBuilder:
    @pytest.mark.asyncio
    @pytest.mark.parametrize("start, finish, frequency, interval", [
        ("2019-01-05 01:00:00", "2019-01-15 01:00:00", Frequency.DAILY, 1),
        ("2019-01-05 01:00:00", "2019-01-15 01:00:00", Frequency.DAILY, 2),
        ("2019-01-05 01:00:00", "2019-02-01 01:00:00", Frequency.WEEKLY, 1),
        ("2019-01-05 01:00:00", "2019-06-01 01:00:00", Frequency.MONTHLY, 1)])
    async def test_toi_build_basic(self, start, finish, frequency, interval):
        datetime_format = '%Y-%m-%d %H:%M:%S'
        toi_configuration = TOIBuilder()
        toi_configuration.build_toi(start=datetime.strptime(start, datetime_format),
                                    finish=datetime.strptime(finish, datetime_format),
                                    description="basic_test_toi")

        toi_configuration.build_recurrence(TOIRuleBuilder.build_rule(frequency=frequency,
                                                                     interval=interval))

        start_ts = Timestamp()
        start_ts.FromDatetime(datetime.strptime(start, datetime_format))
        finish_ts = Timestamp()
        finish_ts.FromDatetime(datetime.strptime(finish, datetime_format))

        toi = toi_configuration.get()
        assert toi.start_local == start_ts
        assert toi.finish_local == finish_ts
        assert toi.recurrences[0].rule == "FREQ={};INTERVAL={}".format(Frequency(frequency).name, interval)
        assert toi.description == "basic_test_toi"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("start, finish, frequency, interval, count", [
        ("2019-01-05 01:00:00", "2019-01-15 01:00:00", Frequency.DAILY, 1, 10),
        ("2019-01-05 01:00:00", "2019-01-15 01:00:00", Frequency.DAILY, 2, 3),
        ("2019-01-05 01:00:00", "2019-02-01 01:00:00", Frequency.WEEKLY, 1, 1),
        ("2019-01-05 01:00:00", "2019-06-01 01:00:00", Frequency.MONTHLY, 1, 3)])
    async def test_toi_build_occurrence(self, start, finish, frequency, interval, count):
        datetime_format = '%Y-%m-%d %H:%M:%S'
        toi_configuration = TOIBuilder()
        toi_configuration.build_toi(start=datetime.strptime(start, datetime_format),
                                    finish=datetime.strptime(finish, datetime_format),
                                    description="toi test occurrence")

        toi_configuration.build_recurrence(TOIRuleBuilder.build_rule(frequency=frequency,
                                                                     interval=interval,
                                                                     count=count))

        start_ts = Timestamp()
        start_ts.FromDatetime(datetime.strptime(start, datetime_format))
        finish_ts = Timestamp()
        finish_ts.FromDatetime(datetime.strptime(finish, datetime_format))

        toi = toi_configuration.get()
        assert toi.start_local == start_ts
        assert toi.finish_local == finish_ts
        assert toi.recurrences[0].rule == "FREQ={};INTERVAL={};COUNT={}".format(Frequency(frequency).name, interval,
                                                                                count)
        assert toi.description == "toi test occurrence"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("start, finish, frequency, interval, until", [
        ("2019-01-05 01:00:00", "2019-01-15 01:00:00", Frequency.DAILY, 1, "20190130T010000Z"),
        ("2019-01-05 01:00:00", "2019-01-15 01:00:00", Frequency.DAILY, 2, "20190130T010000Z"),
        ("2019-01-05 01:00:00", "2019-02-01 01:00:00", Frequency.WEEKLY, 1, "20190230T010000Z"),
        ("2019-01-05 01:00:00", "2019-06-01 01:00:00", Frequency.MONTHLY, 1, "20190630T010000Z")])
    async def test_toi_build_until(self, start, finish, frequency, interval, until):
        datetime_format = '%Y-%m-%d %H:%M:%S'
        toi_configuration = TOIBuilder()
        toi_configuration.build_toi(start=datetime.strptime(start, datetime_format),
                                    finish=datetime.strptime(finish, datetime_format),
                                    description="toi test until")

        toi_configuration.build_recurrence(TOIRuleBuilder.build_rule(frequency=frequency,
                                                                     interval=interval,
                                                                     until=until))

        start_ts = Timestamp()
        start_ts.FromDatetime(datetime.strptime(start, datetime_format))
        finish_ts = Timestamp()
        finish_ts.FromDatetime(datetime.strptime(finish, datetime_format))

        toi = toi_configuration.get()
        assert toi.start_local == start_ts
        assert toi.finish_local == finish_ts
        assert toi.recurrences[0].rule == "FREQ={};INTERVAL={};UNTIL={}".format(Frequency(frequency).name, interval,
                                                                                until)
        assert toi.description == "toi test until"

    @pytest.mark.asyncio
    @pytest.mark.parametrize("start, finish, frequencies, interval", [
        ("2019-01-05 01:00:00", "2019-01-15 01:00:00", [Frequency.DAILY, Frequency.WEEKLY, Frequency.MONTHLY], 1)])
    async def test_toi_build_multiple_recurrence(self, start, finish, frequencies, interval):
        datetime_format = '%Y-%m-%d %H:%M:%S'
        toi_configuration = TOIBuilder()
        toi_configuration.build_toi(start=datetime.strptime(start, datetime_format),
                                    finish=datetime.strptime(finish, datetime_format),
                                    description="toi test until")

        for frequency in frequencies:
            toi_configuration.build_recurrence(TOIRuleBuilder.build_rule(frequency=frequency,
                                                                         interval=interval))

        assert len(toi_configuration.get().recurrences) == len(frequencies)
        start_ts = Timestamp()
        start_ts.FromDatetime(datetime.strptime(start, datetime_format))
        finish_ts = Timestamp()
        finish_ts.FromDatetime(datetime.strptime(finish, datetime_format))

        toi = toi_configuration.get()
        assert toi.start_local == start_ts
        assert toi.finish_local == finish_ts
        for recurrence in toi.recurrences:
            found_it = False
            for frequency in frequencies:
                if recurrence.rule == "FREQ={};INTERVAL={}".format(Frequency(frequency).name, interval):
                    found_it = True
            assert found_it
        assert toi.description == "toi test until"
