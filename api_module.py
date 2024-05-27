from pydantic import BaseModel
import protocol
import pytz
import argparse
import logging
from typing import List
from enum import Enum
import time

from fastapi import FastAPI
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import bittensor as bt
import asyncio
lock = asyncio.Lock()

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    filename='app.log',
                    filemode='a')


RESYNC_METAGRAPH_PERIOD = 15  # in minutes
NETUID = 32


def config() -> bt.config:
    """
    Returns the configuration object.
    """
    parser = argparse.ArgumentParser(
        description="Run the API Server for Subnet 32"
    )
    bt.wallet.add_args(parser)
    bt.subtensor.add_args(parser)
    bt.logging.add_args(parser)
    bt.axon.add_args(parser)

    parser.add_argument("--auth_key",
                        type=str, default="",
                        help="Auth key for authorization.")
    return bt.config(parser)


class SortType(str, Enum):
    EMISSION = "emission"
    INCENTIVE = "incentive"
    UID = "uid"


class RequestObj(BaseModel):
    text: list
    N_AXONS: int = 10
    SORT_TYPE: SortType = SortType.UID
    TIMEOUT: int = 3
    ORDERING: str = "desc"


class AuthKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: RequestObj, call_next):
        given_auth_key = request.headers.get('Auth')
        logging.info(f'Trying to connect with {given_auth_key}')

        if given_auth_key != vali.config.auth_key:
            logging.error(f'Wrong key: {given_auth_key}')
            return JSONResponse(
                status_code=401,
                content={"detail": "Unauthorized"}
            )

        response = await call_next(request)
        return response


scheduler = AsyncIOScheduler(timezone=pytz.utc)

app = FastAPI()
app.add_middleware(AuthKeyMiddleware)


class Validator:
    def __init__(self):
        self.config = config()
        self.initialize_components(first_run=True)

    def initialize_components(self, first_run=False):
        if not first_run:
            previous_block = self.metagraph.block

        self.wallet = bt.wallet(config=self.config)
        self.subtensor = bt.subtensor(config=self.config)
        self.metagraph = bt.metagraph(netuid=NETUID, sync=False, lite=False)
        self.metagraph.sync(subtensor=self.subtensor)

        if not first_run and previous_block == self.metagraph.block:
            logging.critical(
                "METAGRAPH HASNT CHANGED\n"
                f"Last synced block: {previous_block.item()}")
            return

    async def sync_metagraph(self):
        async with lock:
            s = time.time()
            self.initialize_components()
            logging.info(f"Syncing metagraph in {time.time() - s} seconds.")


vali = Validator()


@app.on_event("startup")
def start_scheduler():
    scheduler.add_job(
        vali.sync_metagraph,
        "interval",
        minutes=RESYNC_METAGRAPH_PERIOD
    )
    scheduler.start()


@app.on_event("shutdown")
def shutdown_scheduler():
    scheduler.shutdown()


def get_axons_to_query(
        metagraph: bt.metagraph,
        sort_type: SortType,
        n_axons: int,
        ordering: str
        ) -> List[bt.axon]:
    axons = metagraph.axons

    axons_to_query = []
    for uid in range(len(axons)):
        if not axons[uid].is_serving:
            continue

        if metagraph.validator_permit[uid]:
            if metagraph.S[uid] > 1_000:
                continue

        axons_to_query.append([uid, axons[uid]])

    ordering_type = True if ordering == 'desc' else False
    if sort_type == SortType.EMISSION:
        axons_to_query.sort(key=lambda i: metagraph.E[i[0]],
                            reverse=ordering_type)
    elif sort_type == SortType.INCENTIVE:
        axons_to_query.sort(key=lambda i: metagraph.I[i[0]],
                            reverse=ordering_type)
    elif sort_type == SortType.UID:
        axons_to_query.sort(key=lambda i: i[0], reverse=ordering_type)
    return axons_to_query[:n_axons]


@app.post("/detect/")
async def query_axons_endpoint(request: RequestObj) -> JSONResponse:
    logging.info(f'Incoming request with data: {request.json()}')

    if request.SORT_TYPE not in SortType:
        logging.error('Invalid SORT_TYPE value')
        return JSONResponse(
            content={
                "error":
                    f"Invalid SORT_TYPE value: {request.SORT_TYPE}."
                    "Must be one of {list(SortType.__members__.keys())}"
                },
            status_code=400
        )

    if not (1 <= request.N_AXONS <= 256):
        logging.error('Invalid N_AXONS value')
        return JSONResponse(
            content={
                "error":
                    f"Invalid N_AXONS value: {request.N_AXONS}."
                    "Must be in range [1; 256]"
            },
            status_code=400
        )

    if request.TIMEOUT < 0:
        logging.error('Invalid TIMEOUT value')
        return JSONResponse(
            content={
                "error":
                    f"Invalid TIMEOUT value: {request.N_AXONS}."
                    "Must be greater than 0"
            },
            status_code=400
        )

    if request.ORDERING not in ['asc', 'desc']:
        logging.error('Invalid ORDERING value')
        return JSONResponse(
            content={
                "error":
                    f"Invalid ORDERING value: {request.ORDERING}."
                    "Must be one of the ['asc', 'desc']"
            },
            status_code=400
        )

    axons_info_to_query = get_axons_to_query(
        vali.metagraph,
        request.SORT_TYPE,
        request.N_AXONS,
        request.ORDERING
    )
    axons_to_query = [axon for _, axon in axons_info_to_query]

    logging.info(
        f'Axons to query: {len(axons_to_query)}/{len(vali.metagraph.axons)}')

    d = bt.dendrite(wallet=vali.wallet)

    syn = protocol.TextSynapse(texts=request.text, predictions=[])

    responses = await d(
        axons_to_query,
        syn,
        deserialize=True,
        timeout=request.TIMEOUT)

    logging.info(f'Responses received: {responses}\n\n')
    result = []
    for response, (uid, axon) in zip(responses, axons_info_to_query):
        result.append(
            {
                'coldkey': axon.coldkey,
                'hotkey': axon.hotkey,
                'predictions': response.predictions,
                'uid': uid,
                'emission': vali.metagraph.E[uid].item(),
                'incentive': vali.metagraph.I[uid].item()
            }
        )

    logging.info(f'Answer to user: {result}\n\n')
    return JSONResponse(
        content={
            "responses": result
        },
        status_code=200
    )
