from typing import TYPE_CHECKING

from backbone.io_requests import get_all_info
from dbdie_ml.cropper_swarm import CropperSwarm
from dbdie_ml.schemas.groupings import MatchOut, PlayerOut

if TYPE_CHECKING:
    from PIL import Image


async def process_image(img: "Image") -> MatchOut:
    cppsw = CropperSwarm.from_types(
        [
            ["surv", "killer"],
            ["surv_player", "killer_player"],
        ]
    )

    all_snippet_coords = cppsw.apply(img)  # TODO
    assert len(all_snippet_coords) == 5
    encoded_info = [
        process_snippet(img, sc, id) for id, sc in enumerate(all_snippet_coords)
    ]
    all_info = await get_all_info(encoded_info)
    players = [
        PlayerOut(
            id=id,
            character=all_info["characters"][id],
            perks=all_info["perks"][id],
            item=all_info["item"][id],
            addons=all_info["addons"][id],
            offering=all_info["offering"][id],
            status=all_info["status"][id],
            points=all_info["points"][id],
        )
        for id in range(len(all_info["characters"]))
    ]
    return MatchOut(players=players)
