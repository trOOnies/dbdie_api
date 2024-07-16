from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
from backbone.routers import (
    cropping, perks, addons, characters, offerings, items, players, predict
)

app = FastAPI()

app.include_router(cropping.router)

app.include_router(addons.router)
app.include_router(characters.router)
app.include_router(items.router)
app.include_router(offerings.router)
app.include_router(perks.router)
app.include_router(players.router)

app.include_router(predict.router)

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


@app.get("/")
def root():
    return {"message": "Hello World"}
