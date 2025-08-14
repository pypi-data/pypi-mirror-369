import logging

import pytest
from pyro_client.client.file import FileClient
from x_client.aiohttp import Client as HttpClient
from xync_schema.xtype import BaseAd

from xync_client.Abc.BaseTest import BaseTest
from xync_schema.enums import ExStatus, ExType, ExAction
# from xync_schema.models import Ex, ExStat, Curex, Coinex, Race, Ad
from xync_schema import models
from xync_client.Abc.Ex import BaseExClient
from xync_client.loader import TOKEN


@pytest.mark.asyncio(loop_scope="session")
class TestEx(BaseTest):
    @pytest.fixture
    async def clients(self) -> list[HttpClient]:
        exs = await Ex.filter(status__gt=ExStatus.plan).prefetch_related("pm_reps")
        [await ex for ex in exs if ex.type_ == ExType.tg]
        async with FileClient(TOKEN) as b:
            b: FileClient
            clients: list[BaseExClient] = [ex.client(b) for ex in exs]
            yield clients
        [await cl.close() for cl in clients]

    # 0
    async def test_set_coins(self, clients: list[BaseExClient]):
        for client in clients:
            await client.set_coins()
            t, _ = await models.ExStat.update_or_create({"ok": True}, ex=client.ex, action=ExAction.set_coins)
            assert t.ok, "Coins not set"
            logging.info(f"{client.ex.name}: {ExAction.set_coins.name} - ok")

    # 0
    async def test_set_curs(self, clients: list[BaseExClient]):
        for client in clients:
            await client.set_curs()
            t, _ = await models.ExStat.update_or_create({"ok": True}, ex=client.ex, action=ExAction.set_curs)
            assert t.ok, "Curs not set"
            logging.info(f"{client.ex.name}: {ExAction.set_curs.name} - ok")

    # 0
    async def test_set_pms(self, clients: list[BaseExClient]):
        for client in clients:
            await client.set_pms()
            t, _ = await models.ExStat.update_or_create({"ok": True}, ex=client.ex, action=ExAction.set_pms)
            assert t.ok, "Pms not set"
            logging.info(f"{client.ex.name}: {ExAction.set_pms.name} - ok")

    # 0
    async def test_set_pairs(self, clients: list[BaseExClient]):
        for client in clients:
            await client.set_pairs()
            t, _ = await models.ExStat.update_or_create({"ok": True}, ex=client.ex, action=ExAction.set_pairs)
            assert t.ok, "Pairs not set"
            logging.info(f"{client.ex.name}: {ExAction.set_pairs.name} - ok")

    # # 19
    # async def test_curs(self, clients: list[BaseExClient]):
    #     for client in clients:
    #         curs: dict[str, CurEx] = await client.curs()
    #         ok = self.is_dict_of_objects(curs, CurEx)
    #         t, _ = await ExStat.update_or_create({"ok": ok}, ex=client.ex, action=ExAction.curs)
    #         assert t.ok, "No curs"
    #         logging.info(f"{client.ex.name}: {ExAction.curs.name} - ok")
    #
    # # 20
    # async def test_pms(self, clients: list[BaseExClient]):
    #     for client in clients:
    #         pms: dict[int | str, PmEx] = await client.pms()
    #         ok = self.is_dict_of_objects(pms, PmEx)
    #         t, _ = await ExStat.update_or_create({"ok": ok}, ex=client.ex, action=ExAction.pms)
    #         assert t.ok, "No pms"
    #         logging.info(f"{client.ex.name}: {ExAction.pms.name} - ok")
    #
    # # 21
    # async def test_cur_pms_map(self, clients: list[BaseExClient]):
    #     for client in clients:
    #         cur_pms: MapOfIdsList = await client.cur_pms_map()
    #         ok = self.is_map_of_ids(cur_pms)
    #         t, _ = await ExStat.update_or_create({"ok": ok}, ex=client.ex, action=ExAction.cur_pms_map)
    #         assert t.ok, "No pms for cur"
    #         logging.info(f"{client.ex.name}: {ExAction.cur_pms_map.name} - ok")

    # 22
    # async def test_coins(self, clients: list[BaseExClient]):
    #     for client in clients:
    #         coins: dict[str, CoinEx] = await client.coins()
    #         ok = self.is_dict_of_objects(coins, CoinEx)
    #         t, _ = await ExStat.update_or_create({"ok": ok}, ex=client.ex, action=ExAction.coins)
    #         assert t.ok, "No coins"
    #         logging.info(f"{client.ex.name}: {ExAction.coins.name} - ok")

    # # 23
    # async def test_pairs(self, clients: list[BaseExClient]):
    #     for client in clients:
    #         pairs_buy, pairs_sell = await client.pairs()
    #         ok = self.is_map_of_ids(pairs_buy) and self.is_map_of_ids(pairs_sell)
    #         t, _ = await ExStat.update_or_create({"ok": ok}, ex=client.ex, action=ExAction.pairs)
    #         assert t.ok, "No coins"
    #         logging.info(f"{client.ex.name}: {ExAction.pairs.name} - ok")

    # 24
    async def test_ads(self, clients: list[BaseExClient]):
        for client in clients:
            cur = await models.Curex.filter(cur__ticker="EUR", ex=client.ex).first().values_list("exid", flat=True)
            coin = await models.Coinex.filter(coin__ticker="USDT", ex=client.ex).first().values_list("exid", flat=True)
            ads: list[BaseAd] = await client.ads(coin, cur, False)
            ok = self.is_list_of_objects(ads, BaseAd)
            t, _ = await models.ExStat.update_or_create({"ok": ok}, ex=client.ex, action=ExAction.ads)
            assert t.ok, "No ads"
            logging.info(f"{client.ex.name}: {ExAction.ads.name} - ok")

    async def test_race(self):
        races = await models.Race.all().prefetch_related("road__ad")



        # price_dict = {race.id: race.road.ad.price for race in races}
        # print(price_dict)
        # sorted_dict = dict(sorted(price_dict.items(), key=lambda x: x[1]))
        # print(sorted_dict)
        # for race in races:
        #     print(f"{race.id}: {race.road.ad.price}")
        # for race in races:
        #     print(race.id)
