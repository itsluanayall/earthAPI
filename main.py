import io

from fastapi import FastAPI
from fastapi import File, Response

from rasterio.io import MemoryFile
from rasterio.plot import show

import matplotlib.pyplot as plt

from utils import compute_NDVI

app = FastAPI()

@app.post("/")
async def root():
    return {"message": "Welcome to earthAPI!"}


@app.post("/attributes")
async def attributes(file: bytes = File()):
    with MemoryFile(file) as memfile:
        with memfile.open() as f:
            width = f.width
            height = f.height
            bands = f.count
            crs = f.crs
            bounding_box = f.bounds

    return {
        "size": {"width": width, "height": height},
        "bands": bands,
        "coord_ref_sys": crs.to_string(),
        "bounding_box": bounding_box,
    }


@app.post(
    "/thumbnail",
    responses={200: {"content": {"image/png": {}}}},
    response_class=Response,
)
async def thumbnail(file: bytes = File()):
    with MemoryFile(file) as memfile:
        with memfile.open() as f:
            _, ax = plt.subplots(
                1,
                1,
            )
            show(f, ax=ax, title="Sentinel 2 Satellite Image")
            with io.BytesIO() as buffer:
                plt.savefig(buffer, format="png")
                buffer.seek(0)
                image_bytes = buffer.getvalue()

    return Response(content=image_bytes, media_type="image/png")


@app.post(
    "/ndvi",
    responses={200: {"content": {"image/png": {}}}},
    response_class=Response,
)
async def ndvi(file: bytes = File()):
    with MemoryFile(file) as memfile:
        with memfile.open() as f:
            band_NIR = f.read(8)
            band_red = f.read(4)
            ndvi_array = compute_NDVI(band_NIR=band_NIR, band_red=band_red)
            _, ax = plt.subplots(
                1,
                1,
            )
            show(ndvi_array, ax=ax, title="NDVI")
            with io.BytesIO() as buffer:
                plt.savefig(buffer, format="png")
                buffer.seek(0)
                image_bytes = buffer.getvalue()

    return Response(content=image_bytes, media_type="image/png")
