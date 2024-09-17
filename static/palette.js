const hexToRgb = (hex) => {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);

  if (!result) {
    return null;
  }

  return (
    `rgb(` +
    `${parseInt(result[1], 16)}, ` +
    `${parseInt(result[2], 16)}, ` +
    `${parseInt(result[3], 16)})`
  );
};

const palette = [
  hexToRgb("#1a1c2c"),
  hexToRgb("#5d275d"),
  hexToRgb("#b13e53"),
  hexToRgb("#ef7d57"),
  hexToRgb("#ffcd75"),
  hexToRgb("#a7f070"),
  hexToRgb("#38b764"),
  hexToRgb("#257179"),
  hexToRgb("#29366f"),
  hexToRgb("#3b5dc9"),
  hexToRgb("#41a6f6"),
  hexToRgb("#73eff7"),
  hexToRgb("#f4f4f4"),
  hexToRgb("#94b0c2"),
  hexToRgb("#566c86"),
  hexToRgb("#333c57"),
];

let selectedColor = palette[0];

const getHeartData = (color, centerX, centerY) => {
  const [r, g, b] = getRGBValuesFromRGBString(color);
  return [
    [centerX - 2, centerY - 3, r, g, b],
    [centerX + 2, centerY - 3, r, g, b],

    [centerX - 1, centerY - 2, r, g, b],
    [centerX - 2, centerY - 2, r, g, b],
    [centerX - 3, centerY - 2, r, g, b],
    [centerX + 1, centerY - 2, r, g, b],
    [centerX + 2, centerY - 2, r, g, b],
    [centerX + 3, centerY - 2, r, g, b],

    [centerX, centerY - 1, r, g, b],
    [centerX - 1, centerY - 1, r, g, b],
    [centerX - 2, centerY - 1, r, g, b],
    [centerX - 3, centerY - 1, r, g, b],
    [centerX + 1, centerY - 1, r, g, b],
    [centerX + 2, centerY - 1, r, g, b],
    [centerX + 3, centerY - 1, r, g, b],

    [centerX, centerY, r, g, b],
    [centerX - 1, centerY, r, g, b],
    [centerX - 2, centerY, r, g, b],
    [centerX + 1, centerY, r, g, b],
    [centerX + 2, centerY, r, g, b],

    [centerX, centerY + 1, r, g, b],
    [centerX - 1, centerY + 1, r, g, b],
    [centerX + 1, centerY + 1, r, g, b],

    [centerX, centerY + 2, r, g, b],
  ];
};

const onRandomClick = () => {
  const randomX = Math.floor(Math.random() * gridSize + 1);
  const randomY = Math.floor(Math.random() * gridSize + 1);
  const randomColorIndex = Math.floor(Math.random() * palette.length);
  const randomColor = palette[randomColorIndex];

  const drawCommand = getDrawCommand(
    getHeartData(randomColor, randomX, randomY)
  );

  ws.send(JSON.stringify(drawCommand));
};

const createPalette = () => {
  const paletteButtons = document.querySelector("#palette");

  const setSelectedColor = (event, color) => {
    document
      .querySelector(".palette-button.selected")
      .setAttribute("class", "palette-button");

    event.target.setAttribute("class", "palette-button selected");
    selectedColor = color;
  };

  palette.forEach((color, index) => {
    const paletteButton = document.createElement("div");
    paletteButton.setAttribute("class", "palette-button");
    paletteButton.setAttribute("style", `background-color: ${color};`);
    paletteButton.addEventListener("click", (event) =>
      setSelectedColor(event, color)
    );

    if (index === 0) {
      paletteButton.setAttribute("class", "palette-button selected");
    }

    paletteButtons.appendChild(paletteButton);
  });

  const randomButton = document.getElementById("random");
  randomButton.addEventListener("click", onRandomClick);
};

window.addEventListener("load", createPalette);
