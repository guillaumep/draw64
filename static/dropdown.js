window.addEventListener("load", async () => {
  const select = document.getElementById("images");

  select.onchange = (event) => {
    const imageId = event.target.value;
    loadImage(imageId);
    initWebSocket(imageId);
  };

  await fetch("/images")
    .then(async (result) => {
      if (result.ok) {
        return result.json();
      }
    })
    .then((images) => {
      images.forEach(({ image_id }) => {
        const option = document.createElement("option");
        option.value = image_id;
        option.text = image_id;

        select.appendChild(option);
      });
    });

  const evtSource = new EventSource("/sse/announce");

  evtSource.addEventListener("image_created", (event) => {
    const { image_id } = JSON.parse(event.data).event;
    const option = document.createElement("option");
    option.value = image_id;
    option.text = image_id;
    select.appendChild(option);
  });

  evtSource.addEventListener("image_deleted", (event) => {
    const { image_id } = JSON.parse(event.data).event;
    const option = select.children.find((option) => option.value === image_id);
    if (option) {
      select.removeChild(option);
    }
  });
});
