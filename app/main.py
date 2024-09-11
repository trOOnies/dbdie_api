# from fastapi.middleware.cors import CORSMiddleware
from backbone.options import ENDPOINTS as EP
from backbone.routers.helpers import dbd_version
from backbone.routers.predictables import (
    addons,
    characters,
    items,
    labels,
    matches,
    offerings,
    perks,
    players,
    statuses,
)
from backbone.routers.processes import backup, cropping, predict
from backbone.routers.tags import HELPERS as HELP
from backbone.routers.tags import PREDICTABLES as PRED
from backbone.routers.tags import PROCESSES as PROC
from fastapi import FastAPI

app = FastAPI(
    title="DBDIE API",
    summary="DBD Information Extraction API",
    description="This API lets you process your 💀 Dead By Daylight 💀 matches' endcards.",
)

# TODO
if True:
    app.include_router(addons.router, prefix=EP.ADDONS, tags=[PRED, "addons"])
    app.include_router(
        characters.router, prefix=EP.CHARACTERS, tags=[PRED, "characters"]
    )
    app.include_router(items.router, prefix=EP.ITEMS, tags=[PRED, "items"])
    app.include_router(offerings.router, prefix=EP.OFFERINGS, tags=[PRED, "offerings"])
    app.include_router(perks.router, prefix=EP.PERKS, tags=[PRED, "perks"])
    app.include_router(statuses.router, prefix=EP.STATUSES, tags=[PRED, "statuses"])
    app.include_router(players.router, prefix=EP.PLAYERS, tags=[PRED, "players"])
    app.include_router(dbd_version.router, prefix=EP.DBD_VERSION, tags=[HELP])
    app.include_router(matches.router, prefix=EP.MATCHES, tags=[PRED, "matches"])
    app.include_router(labels.router, prefix=EP.LABELS, tags=[PRED, "labels"])

# TODO
if True:
    app.include_router(cropping.router, prefix=EP.CROP, tags=[PROC])
    app.include_router(predict.router, prefix=EP.PREDICT, tags=[PROC])
    app.include_router(backup.router, prefix=EP.BACKUP, tags=[PROC])


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
