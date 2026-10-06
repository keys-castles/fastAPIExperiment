from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel
# in prod, we need to import all the classes from the other files

# DUMMY REDIS CACHE?
OCR_RESULTS: dict[str, dict] = {}
ENGINEER_DATA: dict[str, dict] = {}

# DUMMY DIMENSIONAL DATA CLASS
class dummy_data(BaseModel):
    header: list[ str ]
    rows: list[list[str | float]]
    img_size: int

# DUMMY ENGINEER DIMENSIONS
class dummy_dimensions(BaseModel):
    row: list[ str | float]


# DUMMY OCR
def dummy_OCR(image_bytes: bytes):
    # in the real OCR module,
    # it would need to populate the following object

    dummy_dimensions = dummy_data(
        header=[ "A", "B", "C"],
        rows=[[0.23, 0.34, 4.5], [0.33, 0.44, 4.7], [0.43, 0.54, 4.9]],
        img_size= len(image_bytes))

    return dummy_dimensions




app = FastAPI()

# ----------------------- FASTAPI ROUTES -----------------------
@app.get("/")
def read_root():
    return {"message": "Team 417 says hello!"}


@app.post("/conversion")
async def generate_dimensions_from_OCR(file: UploadFile = File(...)):
    # recieve the image, route to OCR module asynchronosly
    # once the image has dimensions read, return the dimensions to user in JSON
    if not (file.content_type or "").startswith("image/"):
        raise HTTPException(status_code=400, detail="File is not an image")

    image_bytes = await file.read()
    data = dummy_OCR(image_bytes)

    OCR_RESULTS["testID"] = data.model_dump()


    return data

@app.post("/conversion/start")
async def recieve_engineer_dimensions(payload: dummy_dimensions):
    # recieves the engineers selected row in JSON
    # sends the dimensions and image to the CadQuery gen layer
    # through openAI api key

    if not payload.row:
        raise HTTPException(status_code=422, detail="No row selected")

    ENGINEER_DATA["testID"] = payload.model_dump()

    return {"message": "sent items to API for cad generation"}

@app.get("/progress")
async def begin_progress_updates():
    # initializes the SSE progress updates from each module
    return {"message": "initializing SSE handshakes"}

@app.get("/step")
async def return_validated_step_file():
    # returns the validated step file

    return {"message": "pretend this is a valid STEP file"}
