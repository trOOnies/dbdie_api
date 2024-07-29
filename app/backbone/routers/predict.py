from io import BytesIO
from PIL import Image
from fastapi import APIRouter, UploadFile
from backbone.ml import process_image
from dbdie_ml.schemas import MatchOut

router = APIRouter()


@router.post("", response_model=MatchOut)
async def get_items(img: UploadFile):
    file = await img.read()
    img = Image.open(BytesIO(file))
    match_obj = await process_image(img)
    img.close()
    return match_obj
