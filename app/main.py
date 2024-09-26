"""Main FastAPI API."""

from backbone.routers.predictables import character, item, offering, status
from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware

from backbone.options import ENDPOINTS as EP
from backbone.routers.helpers import dbd_version
from backbone.routers.predictables import (
    addons,
    labels,
    matches,
    perks,
    players,
    rarity,
)
from backbone.routers.processes import backup, cropping, extraction, training
from backbone.routers.tags import HELPERS as HELP
from backbone.routers.tags import PREDICTABLES as PRED
from backbone.routers.tags import PROCESSES as PROC

app = FastAPI(
    title="DBDIE API",
    summary="DBD Information Extraction API",
    description="Process your 💀 Dead By Daylight 💀 matches' endcards.",
)

# TODO
if True:
    app.include_router(addons.router,      prefix=EP.ADDONS,      tags=[PRED, EP.ADDONS[1:]]     )
    app.include_router(character.router,   prefix=EP.CHARACTER,   tags=[PRED, EP.CHARACTER[1:]]  )
    app.include_router(item.router,        prefix=EP.ITEM,        tags=[PRED, EP.ITEM[1:]]       )
    app.include_router(offering.router,    prefix=EP.OFFERING,    tags=[PRED, EP.OFFERING[1:]]   )
    app.include_router(perks.router,       prefix=EP.PERKS,       tags=[PRED, EP.PERKS[1:]]      )
    app.include_router(status.router,      prefix=EP.STATUS,      tags=[PRED, EP.STATUS[1:]]     )
    app.include_router(rarity.router,      prefix=EP.RARITY,      tags=[PRED, EP.RARITY[1:]]     )
    app.include_router(players.router,     prefix=EP.PLAYERS,     tags=[PRED, EP.PLAYERS[1:]]    )
    app.include_router(dbd_version.router, prefix=EP.DBD_VERSION, tags=[HELP]                    )
    app.include_router(matches.router,     prefix=EP.MATCHES,     tags=[PRED, EP.MATCHES[1:]]    )
    app.include_router(labels.router,      prefix=EP.LABELS,      tags=[PRED, EP.LABELS[1:]]     )

# TODO
if True:
    app.include_router(cropping.router,   prefix=EP.CROP,    tags=[PROC])
    app.include_router(training.router,   prefix=EP.TRAIN,   tags=[PROC])
    app.include_router(extraction.router, prefix=EP.EXTRACT, tags=[PROC])
    app.include_router(backup.router,     prefix=EP.BACKUP,  tags=[PROC])


# origins = ["*"]  # ! PLEASE DO NOT LEAVE THIS LIKE THIS IN A PRODUCTION ENV!
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=origins,
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"]
# )

# TODO: Take into account new nulls
# * status: 0
# * characters: 0 All, 1 Killer, 2 Surv
# * everything else: 0 Killer, 1 Surv


@app.get("/health", summary="Health check")
def health():
    return {"status": "OK"}
