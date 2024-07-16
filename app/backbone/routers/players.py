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
        offering=req_wrap("offerings", player.offering_id)
    )
    player_out.check_consistency()
    return player_out
