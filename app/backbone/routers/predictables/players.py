"""Router code for player"""

from backbone.endpoints import get_req
from dbdie_classes.schemas.groupings import PlayerIn, PlayerOut
from fastapi import APIRouter

from backbone.options import ENDPOINTS as EP

router = APIRouter()


@router.post("/{id}", response_model=PlayerOut)
def form_player(
    id: int,
    player: PlayerIn,
):
    player_out = PlayerOut(
        id=id,
        character=get_req(EP.CHARACTER, player.character_id),
        perks=[get_req(EP.PERKS, perk_id) for perk_id in player.perk_ids],
        item=get_req(EP.ITEM, player.item_id),
        addons=[get_req(EP.ADDONS, addon_id) for addon_id in player.addon_ids],
        offering=get_req(EP.OFFERING, player.offering_id),
    )
    player_out.check_consistency()
    return player_out


# @staticmethod
# def to_players(snippets_info: "PlayersInfo") -> list["PlayerOut"]:
#     return [to_player(i, sn_info) for i, sn_info in snippets_info.items()]

# import requests
# from dbdie_classes.base import CropCoods, PlayerId
# from dbdie_classes.schemas.groupings import PlayerIn, PlayerOut

# URL = "http://127.0.0.1:8000"


# def to_player(id: PlayerId, sn_info: CropCoods) -> PlayerOut:
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
