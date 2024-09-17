const gridSize = 64;
const squareSize = 10;
const canvasSize = gridSize * squareSize;

const dpr = 2;

const strokeGrid = (ctx) => {
  ctx.strokeStyle = "#b0b0b0";
  ctx.strokeRect(0, 0, canvas.width / dpr, canvas.height / dpr);
  ctx.beginPath();

  for (let i = 0; i < gridSize; i++) {
    ctx.moveTo(i * squareSize, 0);
    ctx.lineTo(i * squareSize, canvas.height);
    ctx.moveTo(0, i * squareSize);
    ctx.lineTo(canvas.width, i * squareSize);
    ctx.stroke();
  }
};

const drawTiles = (ctx) => {
  for (let i = 0; i < gridSize; i++) {
    for (let j = 0; j < gridSize; j++) {
      const isEvenRow = i % 2 === 0;
      if (j % 2 === 0) {
        ctx.fillStyle = isEvenRow ? "#f2f2f2" : "white";
      } else {
        ctx.fillStyle = isEvenRow ? "white" : "#f2f2f2";
      }

      ctx.fillRect(
        i * squareSize,
        j * squareSize,
        i * squareSize + squareSize,
        j * squareSize + squareSize
      );
    }
  }
};

window.addEventListener("load", async () => {
  const imageData = await fetch("/images/img1/data").then((response) => {
    if (response.ok) {
      return response.json();
    }
  });

  const canvas = document.getElementById("canvas");
  const ctx = canvas.getContext("2d");
  ctx.canvas.width = canvasSize * dpr;
  ctx.canvas.height = canvasSize * dpr;

  ctx.scale(dpr, dpr);
  drawTiles(ctx);
  ctx.setTransform(1, 0, 0, 1, 0, 0);

  imageData.forEach((row, rowIndex) => {
    row.forEach((col, colIndex) => {
      const [r, g, b] = col;

      if (r === 255 && g === 255 && b === 255) {
        return;
      }

      ctx.fillStyle = `rgb(${r}, ${g}, ${b})`;
      ctx.fillRect(
        rowIndex * squareSize * dpr,
        colIndex * squareSize * dpr,
        squareSize * dpr,
        squareSize * dpr
      );
    });
  });

  canvas.addEventListener("pointerdown", onMouseDown);
  canvas.addEventListener("pointermove", onMouseMove);
  canvas.addEventListener("pointerup", onMouseUp);
});

let lastMouseX = -1;
let lastMouseY = -1;
let isMouseDown = false;

const getDrawCommand = (x, y, r, g, b) => ({
  command: {
    command_type: "draw",
    values: [[x, y, r, g, b]],
  },
});

const getMousePosition = (event) => {
  const rect = canvas.getBoundingClientRect();
  const x = Math.floor((event.clientX - rect.left) / squareSize);
  const y = Math.floor((event.clientY - rect.top) / squareSize);

  return [x, y];
};

const getSelectedColor = () =>
  selectedColor
    .replace(/[^\d,]/g, "")
    .split(",")
    .map((v) => parseInt(v, 10));

const sendDrawCommand = (x, y) => {
  const [r, g, b] = getSelectedColor();

  const drawCommand = getDrawCommand(x, y, r, g, b);

  ws.send(JSON.stringify(drawCommand));
};

const onMouseDown = (event) => {
  const [x, y] = getMousePosition(event);
  lastMouseX = x;
  lastMouseY = y;
  isMouseDown = true;

  sendDrawCommand(x, y);
};

const onMouseMove = (event) => {
  if (!isMouseDown) {
    return;
  }

  const [x, y] = getMousePosition(event);

  if (x !== lastMouseX || y !== lastMouseY) {
    lastMouseX = x;
    lastMouseY = y;
    isMouseDown = true;
    sendDrawCommand(x, y);
  }
};

const onMouseUp = () => {
  isMouseDown = false;
};
