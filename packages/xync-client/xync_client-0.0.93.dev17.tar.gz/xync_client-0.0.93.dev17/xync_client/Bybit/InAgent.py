import json
import logging
from datetime import datetime

import websockets
from asyncio import run
from decimal import Decimal

from playwright.async_api import async_playwright
from pyro_client.client.file import FileClient
from xync_client.Abc.PmAgent import PmAgentClient
from xync_schema import models
from xync_schema.enums import UserStatus, OrderStatus

from xync_client.Pms.Payeer import Client
from xync_client.Bybit.etype.order import (
    StatusChange,
    CountDown,
    SellerCancelChange,
    Read,
    Receive,
    OrderFull,
    StatusApi,
)
from xync_client.loader import TOKEN
from xync_client.Abc.InAgent import BaseInAgentClient
from xync_client.Bybit.agent import AgentClient


done = set()


class InAgentClient(BaseInAgentClient):
    agent_client: AgentClient

    async def start_listen(self):
        t = await self.agent_client.ott()
        ts = int(float(t["time_now"]) * 1000)
        await self.ws_prv(self.agent_client.actor.agent.auth["deviceId"], t["result"], ts)

    # 3N: [T] - Уведомление об одобрении запроса на сделку
    async def request_accepted_notify(self) -> int: ...  # id

    async def ws_prv(self, did: str, tok: str, ts: int):
        u = f"wss://ws2.bybit.com/private?appid=bybit&os=web&deviceid={did}&timestamp={ts}"
        async with websockets.connect(u) as websocket:
            auth_msg = json.dumps({"req_id": did, "op": "login", "args": [tok]})
            await websocket.send(auth_msg)

            sub_msg = json.dumps({"op": "subscribe", "args": ["FIAT_OTC_TOPIC", "FIAT_OTC_ONLINE_TOPIC"]})
            await websocket.send(sub_msg)
            sub_msg = json.dumps({"op": "input", "args": ["FIAT_OTC_TOPIC", '{"topic":"SUPER_DEAL"}']})
            await websocket.send(sub_msg)
            sub_msg = json.dumps({"op": "input", "args": ["FIAT_OTC_TOPIC", '{"topic":"OTC_ORDER_STATUS"}']})
            await websocket.send(sub_msg)
            sub_msg = json.dumps({"op": "input", "args": ["FIAT_OTC_TOPIC", '{"topic":"WEB_THREE_SELL"}']})
            await websocket.send(sub_msg)
            sub_msg = json.dumps({"op": "input", "args": ["FIAT_OTC_TOPIC", '{"topic":"APPEALED_CHANGE"}']})
            await websocket.send(sub_msg)

            sub_msg = json.dumps({"op": "subscribe", "args": ["fiat.cashier.order"]})
            await websocket.send(sub_msg)
            sub_msg = json.dumps({"op": "subscribe", "args": ["fiat.cashier.order-eftd-complete-privilege-event"]})
            await websocket.send(sub_msg)
            sub_msg = json.dumps({"op": "subscribe", "args": ["fiat.cashier.order-savings-product-event"]})
            await websocket.send(sub_msg)
            sub_msg = json.dumps({"op": "subscribe", "args": ["fiat.deal-core.order-savings-complete-event"]})
            await websocket.send(sub_msg)

            sub_msg = json.dumps({"op": "subscribe", "args": ["FIAT_OTC_TOPIC", "FIAT_OTC_ONLINE_TOPIC"]})
            await websocket.send(sub_msg)
            while resp := await websocket.recv():
                if data := json.loads(resp):
                    upd, order_db = None, None
                    logging.info("New update:")
                    match data.get("topic"):
                        case "OTC_ORDER_STATUS":
                            match data["type"]:
                                case "STATUS_CHANGE":
                                    upd = StatusChange.model_validate(data["data"])
                                    order = self.agent_client.api.get_order_details(orderId=upd.id)
                                    order = OrderFull.model_validate(order["result"])
                                    order_db = await models.Order.get_or_none(
                                        exid=order.id, ad__exid=order.itemId
                                    ) or await self.agent_client.create_order(order)
                                    match upd.status:
                                        case StatusApi.created:
                                            # order_db = await self.agent_client.create_order(order)
                                            logging.info(f"Order {order.id} created at {order.createDate}")
                                        case StatusApi.wait_for_buyer:
                                            if upd.side == 0:  # ждем когда покупатель оплатит
                                                pma, cdx = await self.get_pma_by_cdex(order)
                                                am, tid = pma.check_in(Decimal(order.amount), cdx.cred.pmcur.cur.ticker)
                                                if tid and tid not in done:
                                                    done.add(tid)
                                                    self.agent_client.api.release_assets(orderId=upd.id)
                                                    logging.info(
                                                        f"Order {order.id} created, paid before #{tid}:{am} at {order.createDate}, and RELEASED at {datetime.now()}"
                                                    )
                                                else:
                                                    logging.info(
                                                        f"Order {order.id} created at {order.createDate} but no paid yet"
                                                    )
                                            elif upd.side == 1:  # я покупатель - ждем мою оплату
                                                pma = self.pmacs.get(order.paymentTermList[0].paymentType)
                                                int_am = int(Decimal(order.amount))
                                                await pma.send(
                                                    dest=order.paymentTermList[0].accountNo,
                                                    amount=int_am,
                                                    cur=cdx.cred.pmcur.cur.ticker,
                                                )
                                                logging.warning(f"Order {order.id} PAID at {datetime.now()}: {int_am}")
                                            else:
                                                ...
                                            # todo: check is always canceling
                                            await order_db.update_from_dict({"status": OrderStatus.canceled}).save()
                                            logging.info(f"Order {order.id} canceled at {datetime.now()}")
                                        case StatusApi.appealed:
                                            # todo: appealed by WHO? щас наугад стоит by_seller
                                            await order_db.update_from_dict(
                                                {
                                                    "status": OrderStatus.appealed_by_seller,
                                                    "appealed_at": round(float(order.updateDate), 3),
                                                }
                                            ).save()
                                            logging.info(f"Order {order.id} appealed at {order_db.appealed_at}")
                                        case StatusApi.canceled:
                                            await order_db.update_from_dict({"status": OrderStatus.canceled}).save()
                                            logging.info(f"Order {order.id} canceled at {datetime.now()}")
                                        case StatusApi.completed:
                                            await order_db.update_from_dict(
                                                {
                                                    "status": OrderStatus.completed,
                                                    "confirmed_at": round(float(order.updateDate), 3),
                                                }
                                            ).save()
                                            logging.info(f"Order {order.id} completed at {order_db.confirmed_at}")
                                        case StatusApi.wait_for_seller:
                                            await order_db.update_from_dict(
                                                {
                                                    "status": OrderStatus.paid,
                                                    "payed_at": round(float(order.transferDate), 3),
                                                }
                                            ).save()
                                            logging.info(f"Order {order.id} payed at {order_db.payed_at}")
                                        case _:
                                            logging.warning(f"Order {order.id} UNKNOWN STATUS {datetime.now()}")
                                case "COUNT_DOWN":
                                    upd = CountDown.model_validate(data["data"])
                                case _:
                                    self.listen(data)
                        case "OTC_USER_CHAT_MSG":
                            match data["type"]:
                                case "RECEIVE":
                                    upd = Receive.model_validate(data["data"])

                                case "READ":
                                    upd = Read.model_validate(data["data"])
                                    # if upd.status not in (StatusWs.created, StatusWs.canceled, 10, StatusWs.completed):
                                    if upd.orderStatus in (
                                        StatusApi.wait_for_buyer_pay,
                                    ):  # todo: тут приходит ордер.статус=10, хотя покупатель еще не нажал оплачено
                                        order = self.agent_client.api.get_order_details(orderId=upd.orderId)["result"]
                                        order = OrderFull.model_validate(order)

                                case "CLEAR":
                                    pass
                                case _:
                                    self.listen(data)
                        case "OTC_USER_CHAT_MSG_V2":
                            # match data["type"]:
                            #     case "RECEIVE":
                            #         upd = Receive.model_validate(data["data"])
                            #     case "READ":
                            #         upd = Read.model_validate(data["data"])
                            #     case "CLEAR":
                            #         pass
                            #     case _:
                            #         self.listen(data)
                            continue
                        case "SELLER_CANCEL_CHANGE":
                            upd = SellerCancelChange.model_validate(data["data"])
                        case None:
                            if not data.get("success"):
                                logging.error(data, "NOT SUCCESS!")
                            else:
                                continue  # success login, subscribes, input
                        case _:
                            logging.warning(data, "UNKNOWN TOPIC")
                    if not upd:
                        logging.error(data, "NOT PROCESSED UPDATE")

    async def get_pma_by_cdex(self, order: OrderFull) -> tuple[PmAgentClient, models.CredEx]:
        cdxs = await models.CredEx.filter(
            ex=self.agent_client.ex_client.ex,
            exid__in=[ptl.id for ptl in order.paymentTermList],
            cred__person=self.agent_client.actor.person,
        ).prefetch_related("cred__pmcur__cur")
        pmas = [pma for cdx in cdxs if (pma := self.pmacs.get(cdx.cred.pmcur.pm_id))]
        if not len(pmas):
            logging.error(order.paymentTermList, "No pm_agents")
        if len(pmas) > 1:
            logging.error(order.paymentTermList, ">1 pm_agents")
        return pmas[0], cdxs[0]

    @staticmethod
    def listen(data: dict | None):
        # print(data)
        ...


async def main():
    from x_model import init_db
    from xync_client.loader import TORM

    _ = await init_db(TORM, True)
    logging.basicConfig(level=logging.INFO)

    actor = (
        await models.Actor.filter(
            ex_id=9,
            agent__auth__isnull=False,
            person__user__status=UserStatus.ACTIVE,
            person__user__pm_agents__isnull=False,
        )
        .prefetch_related("ex", "agent", "person__user__pm_agents")
        .first()
    )

    async with FileClient(TOKEN) as b:
        cl: InAgentClient = actor.in_client(b)
        # await cl.agent_client.export_my_ads()
        payeer_cl = Client(actor.person.user.username_id)
        for pma in actor.person.user.pm_agents:
            cl.pmacs[pma.pm_id] = await payeer_cl.start(await async_playwright().start(), False)

        _ = await cl.start_listen()
        await cl.agent_client.close()


if __name__ == "__main__":
    run(main())
