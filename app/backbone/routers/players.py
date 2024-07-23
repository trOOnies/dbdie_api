from fastapi import APIRouter
from dbdie_ml import schemas
from backbone.endpoints import req_wrap

router = APIRouter(prefix="/players", tags=["players"])


@router.post("/{id}", response_model=schemas.PlayerOut)
def form_player(
    id: int,
    player: schemas.PlayerIn,
):
    player_out = schemas.PlayerOut(
        id=id,
        character=req_wrap("characters", player.character_id),
        perks=[req_wrap("perks", perk_id) for perk_id in player.perk_ids],
        item=req_wrap("items", player.item_id),
        addons=[req_wrap("addons", addon_id) for addon_id in player.addon_ids],
        offering=req_wrap("offerings", player.offering_id),
    )
    player_out.check_consistency()
    return player_out


# @staticmethod
# def to_players(snippets_info: "AllSnippetInfo") -> list["PlayerOut"]:
#     return [to_player(i, sn_info) for i, sn_info in snippets_info.items()]

# import requests
# from dbdie_ml.classes import SnippetInfo, PlayerId
# from dbdie_ml.schemas import PlayerIn, PlayerOut

# URL = "http://127.0.0.1:8000"


# def to_player(id: PlayerId, sn_info: SnippetInfo) -> PlayerOut:
#     player_in = PlayerIn(
#         character_id=sn_info.character_id,
#         perk_ids=sn_info.perks_ids,
#         item_id=sn_info.item_id,
#         addon_ids=sn_info.addons_ids,
#         offering_id=sn_info.offering_id
#     )
#     player_out = requests.get(
#         f"{URL}/form_player",
#         params={
#             "id": id,
#             "player": player_in
#         }
#     )
#     return PlayerOut(**player_out.json())
