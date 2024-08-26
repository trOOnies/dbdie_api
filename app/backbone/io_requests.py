import asyncio
import aiohttp
from dbdie_ml.classes.base import EncodedInfo
from dbdie_ml.schemas.predictables import StatusOut

from backbone.config import endp


async def fetch(session, url):
    async with session.get(url) as response:
        return await response.json()


async def fetch_list(item_type: str, ids: list[int]):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch(session, endp(f"/{item_type}/{id}")) for id in ids]
        items = await asyncio.gather(*tasks)
    return items


async def get_all_info(ei_list: list[EncodedInfo]) -> dict:
    characters = await fetch_list("characters", [ei[0] for ei in ei_list])
    item = await fetch_list("items", [ei[2] for ei in ei_list])
    offering = await fetch_list("offerings", [ei[4] for ei in ei_list])
    status = [StatusOut(id=2, name="killed", is_dead=True) for _ in range(4)] + [
        StatusOut(id=0, name="killer", is_dead=None)
    ]
    points = [ei[6] for ei in ei_list]

    perks = []
    addons = []
    for ei in ei_list:
        perks_add = await fetch_list("perks", ei[1])
        perks.append(perks_add)
        addons_add = await fetch_list("addons", ei[3])
        addons.append(addons_add)

    return {
        "characters": characters,
        "perks": perks,
        "item": item,
        "addons": addons,
        "offering": offering,
        "status": status,
        "points": points,
    }
