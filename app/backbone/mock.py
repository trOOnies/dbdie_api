from typing import TYPE_CHECKING

from dbdie_ml.classes.base import PlayerInfo

if TYPE_CHECKING:
    from dbdie_ml.classes.base import CropCoords
    from PIL import Image

MOCK_SNIPPETS_COORDS = [(67 + i * 117, 217, 67 + (i + 1) * 117, 897) for i in range(5)]


class MockSnippetModel:
    @staticmethod
    def predict(img: "Image") -> list["CropCoords"]:
        return MOCK_SNIPPETS_COORDS


class MockKillerModel:
    @staticmethod
    def predict(snippet: "CropCoords") -> "PlayerInfo":
        return PlayerInfo(
            character_id=10,
            perks_ids=(10, 11, 12, 13),
            item_id=1,
            addons_ids=(10, 11),
            offering_id=2,
            status_id=2,
            points=10_000,
        )


class MockPlayerModel:
    @staticmethod
    def predict(snippet: "CropCoords") -> "PlayerInfo":
        return PlayerInfo(
            character_id=40,
            perks_ids=(10, 11, 12, 13),
            item_id=1,
            addons_ids=(10, 11),
            offering_id=2,
            status_id=2,
            points=10_000,
        )
