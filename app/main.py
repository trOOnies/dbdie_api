# from fastapi.middleware.cors import CORSMiddleware
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
from backbone.routers.processes import backup, cropping, cvat_code, predict
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
    app.include_router(addons.router, prefix="/addons", tags=[PRED, "addons"])
    app.include_router(
        characters.router, prefix="/characters", tags=[PRED, "characters"]
    )
    app.include_router(items.router, prefix="/items", tags=[PRED, "items"])
    app.include_router(offerings.router, prefix="/offerings", tags=[PRED, "offerings"])
    app.include_router(perks.router, prefix="/perks", tags=[PRED, "perks"])
    app.include_router(statuses.router, prefix="/statuses", tags=[PRED, "statuses"])
    app.include_router(players.router, prefix="/players", tags=[PRED, "players"])
    app.include_router(dbd_version.router, prefix="/dbd-version", tags=[HELP])
    app.include_router(matches.router, prefix="/matches", tags=[PRED, "matches"])
    app.include_router(labels.router, prefix="/labels", tags=[PRED, "labels"])

# TODO
if True:
    app.include_router(cropping.router, prefix="/crop", tags=[PROC])
    app.include_router(cvat_code.router, prefix="/cvat", tags=[PROC])
    app.include_router(predict.router, prefix="/predict", tags=[PROC])
    app.include_router(backup.router, prefix="/backup", tags=[PROC])


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
