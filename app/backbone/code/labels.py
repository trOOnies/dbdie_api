def player_to_labels(player: dict) -> dict:
    """Convert dict format from `LabelsCreate` schema's to `Labels` model's"""
    labels = (
        {
            "player_id": player["id"],
            "points": player["points"],
        }
        | {k[:-3]: v for k, v in player.items() if k.endswith("_id")}
        | {f"perk_{i}": v for i, v in enumerate(player["perk_ids"])}
        | {f"addon_{i}": v for i, v in enumerate(player["addon_ids"])}
    )
    return labels
