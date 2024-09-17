const baseURL = location.origin
  .replace("http:", "ws:")
  .replace("https:", "wss:");

let ws;

const initWebSocket = (imageId) => {
  ws?.close();
  ws = new WebSocket(`${baseURL}/ws/images/${imageId}`);
  ws.onmessage = onMessage;
};

const onMessage = (event) => {
  const data = JSON.parse(event.data);

  data.event.command.values.forEach(([x, y, r, g, b]) => {
    const canvas = document.getElementById("canvas");
    const ctx = canvas.getContext("2d");
    ctx.fillStyle = `rgb(${r}, ${g}, ${b})`;
    ctx.fillRect(
      x * squareSize * dpr,
      y * squareSize * dpr,
      squareSize * dpr,
      squareSize * dpr
    );
  });
};

initWebSocket("default");
