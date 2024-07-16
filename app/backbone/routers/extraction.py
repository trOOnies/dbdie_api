import os
import pandas as pd
from PIL import Image
from fastapi import APIRouter, status
from backbone.functions import save_esp_info

router = APIRouter(prefix="/extraction", tags=["extraction"])


@router.get("")
def extract_info():
    img_fnames = os.listdir("img")
    for img_fname in img_fnames:
        img = Image.open(img_fname)
        # esp_info = process_dbd_esp(img)
        esp_info = pd.DataFrame()
        del img
        save_esp_info(esp_info, "out")

    return status.HTTP_200_OK
