from fastapi import (
    APIRouter,
    HTTPException,
    Response,
    status,
)
from fastapi.responses import HTMLResponse

from draw64.image import Image, ImageData
from draw64.image_collection import ImageIDAlreadyExistsException
from draw64.image_id import ImageID, ValidatedImageID
from draw64.state import pubsub, collection
from draw64.update_image_request import UpdateImageRequest
from draw64.event_factory import (
    make_image_created_message,
    make_image_deleted_message,
    make_image_updated_message,
)

router = APIRouter()


html = """
<!DOCTYPE html>
<html>
    <head>
        <title>Chat</title>
    </head>
    <body>
        <canvas style="width: 640px; height: 640px;" id="canvas" width="1280" height="1280"></canvas>
        <div style="width: 30px; height: 30px; background-color: red; border-radius: 15px;" onclick="setSelectedColor([225, 0, 0]);"></div>
        <div style="width: 30px; height: 30px; background-color: rgb(0, 0, 255); border-radius: 15px;" onclick="setSelectedColor([0, 0, 255]);"></div>
        <div style="width: 30px; height: 30px; background-color: rgb(0, 255, 0); border-radius: 15px;" onclick="setSelectedColor([0, 255, 0]);"></div>
        <ul id='messages'>
        </ul>
        <script>
            let selectedColor = 'rgb(86, 126, 193)';
            const setSelectedColor = (color) => {
                selectedColor = `rgb(${color[0]}, ${color[1]}, ${color[2]})`
            };

            const gridSize = 64;
            const squareSize = 10;
            const canvasSize = gridSize * squareSize;
            const dpr = 2;
            const canvas = document.getElementById('canvas');
        
            const ctx = canvas.getContext('2d');
            ctx.canvas.width = canvasSize * dpr;
            ctx.canvas.height = canvasSize * dpr;
            ctx.scale(dpr, dpr);
            
            
            ctx.strokeStyle = '#b0b0b0';
            ctx.strokeRect(0, 0, canvas.width / dpr, canvas.height / dpr);
            ctx.beginPath();
            
            for (let i = 0; i < gridSize; i++) {
                ctx.moveTo(i * squareSize, 0);
                ctx.lineTo(i * squareSize, canvas.height);
                ctx.moveTo(0, i * squareSize);
                ctx.lineTo(canvas.width, i * squareSize);
                ctx.stroke();
            }
            ctx.setTransform(1, 0, 0, 1, 0, 0);

            const onCanvasClick = (event) => {
                const rect = canvas.getBoundingClientRect();
                const x = Math.floor((event.clientX - rect.left) / squareSize);
                const y = Math.floor((event.clientY - rect.top) / squareSize);
                const [r, g, b] = selectedColor.replace(/[^\d,]/g, '').split(',').map((v) => parseInt(v, 10));

                const drawCommand = { 
                    "command": {
                        "command_type": "draw", 
                        "values": [[x, y, r, g, b]]
                    }
                }
    
                ws.send(JSON.stringify(drawCommand));
            };

            canvas.addEventListener('click', onCanvasClick);

            var ws = new WebSocket("ws://localhost:8000/ws/img1");
            ws.onmessage = function(event) {
                const data = JSON.parse(event.data)
                const [x, y, r, g, b]  = data.event.command.values[0];
                ctx.fillStyle = `rgb(${r}, ${g}, ${b})`;
                ctx.fillRect(x * squareSize * dpr, y * squareSize * dpr, squareSize * dpr, squareSize * dpr);
            };

            function sendMessage(event) {
                var input = document.getElementById("messageText")
                ws.send(input.value)
                input.value = ''
                event.preventDefault()
            }
        </script>
    </body>
</html>
"""


@router.get("/")
async def get():
    return HTMLResponse(html)


@router.get("/images")
async def get_images_list() -> list[Image]:
    return list(collection.values())


@router.post("/images", status_code=status.HTTP_201_CREATED)
async def create_image() -> Image:
    image = collection.create_image()
    pubsub.broadcast_all(make_image_created_message(image))
    return image


@router.post(
    "/images/{image_id}",
    status_code=status.HTTP_201_CREATED,
    responses={status.HTTP_409_CONFLICT: {"description": "Image ID already exists."}},
)
async def create_image_with_id(image_id: ImageID) -> Image:
    """
    Create an image, providing an ID.
    """
    try:
        image = collection.create_image(image_id)
        pubsub.broadcast_all(make_image_created_message(image))
        return image
    except ImageIDAlreadyExistsException:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Image ID already exists."
        )


@router.get(
    "/images/{image_id}.png",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Image ID does not exist."}},
)
async def get_image_as_png(image_id: ValidatedImageID):
    return Response(content=collection[image_id].to_png(), media_type="image/png")


@router.get(
    "/images/{image_id}",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Image ID does not exist."}},
)
async def get_image(image_id: ValidatedImageID) -> Image:
    return collection[image_id]


@router.get(
    "/images/{image_id}/data",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Image ID does not exist."}},
)
async def get_image_data(image_id: ValidatedImageID) -> ImageData:
    return collection[image_id].data


@router.put("/images/{image_id}")
async def update_image(image_id: ValidatedImageID, update_request: UpdateImageRequest):
    collection[image_id].update(update_request.command)
    pubsub.broadcast(image_id, make_image_updated_message(image_id, update_request))


@router.delete(
    "/images/{image_id}",
    responses={status.HTTP_404_NOT_FOUND: {"description": "Image ID does not exist."}},
)
async def delete_image(image_id: ValidatedImageID):
    pubsub.broadcast_all(make_image_deleted_message(collection[image_id]))
    del collection[image_id]
