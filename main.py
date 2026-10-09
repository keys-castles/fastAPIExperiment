from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import StreamingResponse, FileResponse
from pydantic import BaseModel, Field
from typing import Optional
from pathlib import Path
import asyncio
import json
# in prod, we need to import all the classes from the other files

# DUMMY REDIS CACHE?
OCR_RESULTS: dict[str, dict] = {}
ENGINEER_DATA: dict[str, dict] = {}

# DUMMY DIMENSIONAL PART CLASS
class part_dummy(BaseModel):
    part_number: str
    specifications: dict[str, str] = Field(default_factory=dict)

# DUMMY ENGINEER DIMENSIONS
class table_dummy(BaseModel):
    table_name: Optional[str] = None
    header_rows: int = 1
    parts: list[part_dummy] = Field(default_factory=list)

class table_data_dummy(BaseModel):
    tables: list[table_dummy] = Field(default_factory=list)


# DUMMY OCR
def dummy_OCR(image_bytes: bytes):
    # in the real OCR module,
    # it would need to populate the following object

    part1 = part_dummy(
        part_number="X-1",
        specifications= {"A": "12", "B": "12", "C": "12"}
        )

    part2 = part_dummy(
            part_number="X-2",
            specifications= {"A": "14", "B": "14", "C": "14"}
            )

    dummy_table = table_dummy(
        table_name="test",
        header_rows=1,
        parts= [part1, part2]
        )

    dummy_tables = table_data_dummy(
        tables=[dummy_table]

    )

    return dummy_tables

# DUMMY PROGRESS HANDLER
async def progress_generator():
    #  just a for loop that sends data like numerical progress
    #  and some flavor text
    flav_text = ["Procrastinating for just a few more seconds...",
                 "Adding artificial delay to look important...",
                 "Generating more flavor text...",
                 "Looking for the API key...",
                 "Whirling and dhirling...",
                 "Chasing wild geese...",
                 "Twiddling thumbs...",
                 "Flavor text.",

    ] 

    for i in range(100):

        txt = flav_text[i%8]
        payload = {"progress": i, "flavor-text": txt}
        yield f"data: {json.dumps(payload)}\n\n"
        await asyncio.sleep(1)

MODELS = Path("STEP")



app = FastAPI()

# ----------------------- FASTAPI ROUTES -----------------------
#  note, we will have to rewrite this to OOP style routes
@app.get("/")
def read_root():
    # delete in prod
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
async def recieve_engineer_dimensions(payload: part_dummy):
    # recieves the engineers selected row in JSON
    # sends the dimensions and image to the CadQuery gen layer
    # through openAI api key

    if not payload.specifications:
        raise HTTPException(status_code=422, detail="No row selected")

    ENGINEER_DATA["testID"] = payload.model_dump()

    return {"message": "sent items to API for cad generation"}

@app.get("/progress")
async def begin_progress_updates():
    # initializes the SSE progress updates from each module
    return StreamingResponse(
        progress_generator(),
        media_type="text/event-stream",
        headers = {"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )

@app.get("/step")
async def return_validated_step_file():
    # returns the validated step file
    # this is for a single STP file, in prod
    # change to something that can serve the STP
    # file from the output folder?
    path = ( MODELS / "140270.stp").resolve()
    if MODELS.resolve() not in path.parents or not path.exists():
        raise HTTPException(404, "Model not found")
    
    return FileResponse(path, media_type="application/step", filename="140270.stp")
