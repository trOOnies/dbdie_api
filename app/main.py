from fastapi import FastAPI

# from fastapi.middleware.cors import CORSMiddleware
from backbone.routers import (
    addons,
    backup,
    characters,
    cropping,
    cvat_code,
    dbd_version,
    items,
    offerings,
    perks,
    players,
    predict,
    status,
)

app = FastAPI(
    title="DBDIE API",
    summary="DBD Information Extraction API",
    description="This API lets you process your 💀 Dead By Daylight 💀 matches' endcards.",
)

# TODO
if True:
    app.include_router(addons.router, prefix="/addons", tags=["predictables", "addons"])
    app.include_router(
        characters.router, prefix="/characters", tags=["predictables", "characters"]
    )
    app.include_router(items.router, prefix="/items", tags=["predictables", "items"])
    app.include_router(
        offerings.router, prefix="/offerings", tags=["predictables", "offerings"]
    )
    app.include_router(perks.router, prefix="/perks", tags=["predictables", "perks"])
    app.include_router(status.router, prefix="/status", tags=["predictables", "status"])
    app.include_router(
        players.router, prefix="/players", tags=["predictables", "players"]
    )
    app.include_router(dbd_version.router, prefix="/dbd-version", tags=["helpers"])

# TODO
if True:
    app.include_router(cropping.router, prefix="/crop", tags=["processes"])
    app.include_router(cvat_code.router, prefix="/cvat", tags=["processes"])
    app.include_router(predict.router, prefix="/predict", tags=["processes"])
    app.include_router(backup.router, prefix="/backup", tags=["processes"])


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


@app.get("/health")
def health():
    return {"status": "OK"}
