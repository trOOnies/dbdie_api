from typing import TYPE_CHECKING

import requests
import pandas as pd
from dbdie_ml.classes.base import FullModelType
from backbone.code.labels import concat_player_types, player_to_labels
from backbone.config import endp
from backbone.database import get_db
from backbone.models import Labels
from dbdie_ml.options import COMMON_FMT, KILLER_FMT, SURV_FMT
from dbdie_ml.paths import LABELS_FD_RP, absp
from dbdie_ml.schemas.groupings import LabelsCreate, LabelsOut, PlayerIn
from fastapi import APIRouter, Depends, status, Response
from fastapi.exceptions import HTTPException

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

router = APIRouter()

ALL_FMT = list(set(COMMON_FMT.ALL) | set(KILLER_FMT.ALL) | set(SURV_FMT.ALL))


@router.get("/count", response_model=int)
def count_labels(db: "Session" = Depends(get_db)):
    query = db.query(Labels.match_id)
    return query.count()


@router.get("", response_model=LabelsOut)
def get_labels(
    match_id: int,
    player_id: int,
    db: "Session" = Depends(get_db),
):
    print("HEY")
    labels = (
        db.query(Labels)
        .filter(Labels.match_id == match_id)
        .filter(Labels.player_id == player_id)
        .first()
    )
    if labels is None:
        raise HTTPException(
            status.HTTP_404_NOT_FOUND,
            f"Labels with the id ({match_id}, {player_id}) were not found",
        )
    labels = LabelsOut(
        match_id=labels.match_id,
        player=PlayerIn.from_labels(labels),
        date_modified=labels.date_modified,
    )
    return labels


@router.post("", response_model=LabelsOut)
def create_labels(
    labels: LabelsCreate,
    db: "Session" = Depends(get_db),
):
    new_labels = labels.model_dump()
    new_labels = new_labels | player_to_labels(new_labels["player"])
    del new_labels["player"]
    new_labels = Labels(**new_labels)

    db.add(new_labels)
    db.commit()
    db.refresh(new_labels)

    resp = requests.get(
        endp("/labels"),
        params={
            "match_id": new_labels.match_id,
            "player_id": new_labels.player_id,
        },
    )
    if resp.status_code != status.HTTP_200_OK:
        raise HTTPException(resp.status_code, resp.json()["detail"])
    return resp.json()


@router.post("", status_code=status.HTTP_200_OK)
def batch_create_labels(fmts: list[FullModelType], filename: str):
    """Create labels from label CSVs."""
    # TODO: Fix
    assert fmts, "Full model types can't be empty"
    assert all(fmt in ALL_FMT for fmt in fmts)

    # TODO
    # * Additional temporary filter
    assert all(
        fmt in {KILLER_FMT.PERKS, SURV_FMT.PERKS, KILLER_FMT.CHARACTER, SURV_FMT.CHARACTER}
        for fmt in fmts
    )

    dfs = {
        fmt: pd.read_csv(
            absp(LABELS_FD_RP, f"{fmt}/{filename}"),
            usecols=["name", "label_id"],
        )
        for fmt in fmts
    }

    # One per player crop -> (name, player_id, <obj>)
    for c in [SURV_FMT.CHARACTER, KILLER_FMT.CHARACTER]:
        if c in dfs:
            dfs[c]["player_id"] = dfs[c]["name"].str[-7]
            dfs[c] = dfs[c].astype({"player_id": int})
            dfs[c]["name"] = (
                dfs[c]["name"].str[:-7]
                + dfs[c]["name"].str[-4:]
            )
            dfs[c] = dfs[c].rename({"label_id": "character"}, axis=1)

    concat_player_types(
        dfs,
        SURV_FMT.CHARACTER,
        KILLER_FMT.CHARACTER,
        new_fmt="character",
    )

    # Many per player crop -> (name, player_id, <obj>_i)
    for c in [SURV_FMT.PERKS, KILLER_FMT.PERKS]:
        if c in dfs:
            dfs[c]["player_id"] = dfs[c]["name"].str[-7]
            dfs[c]["perk_id"] = dfs[c]["name"].str[-5]
            dfs[c]["name"] = (
                dfs[c]["name"].str[:-7]
                + dfs[c]["name"].str[-4:]
            )

            dfs[c] = dfs[c].rename({"perk_id": "perk"}, axis=1)
            dfs[c] = dfs[c].astype({"player_id": int, "perk": int})

            dfs[c] = pd.get_dummies(dfs[c], columns=["perk"])
            assert "perk" not in dfs[c].columns

    concat_player_types(
        dfs,
        SURV_FMT.PERKS,
        KILLER_FMT.PERKS,
        new_fmt="perks",
    )

    dfs = {fmt: df.set_index("name", drop=True) for fmt, df in dfs.items()}

    is_first = True
    for fmt in dfs:
        if is_first:
            joined_df = dfs[fmt].copy()
            is_first = False
        else:
            joined_df = joined_df.join(dfs[fmt])
        dfs[fmt] = None
    del dfs

    joined_df["match_id"] = joined_df.index.map(
        lambda f: requests.get(
            endp("/matches/id"),
            params={"filename": f},
        ).json(),
    )
    joined_df = joined_df.drop("name", axis=1)

    for _, row in joined_df.iterrows():
        requests.post(
            endp("/labels"),
            json={
                "match_id": row["match_id"],
                "player": {
                    "id": row["player_id"],
                    "character_id": row["character"],
                    "perk_ids": [row[f"perk_{i}"] for i in range(4)],
                    "item_id": None,
                    "addon_ids": None,
                    "offering_id": None,
                    "status_id": None,
                    "points": None,
                },
            },
        )

    return Response(status_code=status.HTTP_200_OK)
