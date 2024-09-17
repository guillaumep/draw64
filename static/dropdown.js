const initDropdown = async () => {
  const select = document.getElementById("images");

  select.onchange = (event) => {
    const imageId = event.target.value;
    loadImage(imageId);
    initWebSocket(imageId);
  };

  const addOption = ({ image_id }) => {
    const existingOption = document.getElementById(`image-${image_id}`);
    if (existingOption) {
      return;
    }

    const option = document.createElement("option");
    option.value = image_id;
    option.text = image_id;
    option.id = `image-${image_id}`;

    select.appendChild(option);
  };

  const evtSource = new EventSource("/sse/announce");

  evtSource.addEventListener("image_created", (event) => {
    addOption(JSON.parse(event.data).event);
  });

  evtSource.addEventListener("image_deleted", (event) => {
    const { image_id } = JSON.parse(event.data).event;
    const option = document.getElementById(`image-${image_id}`);
    if (option) {
      select.removeChild(option);
    }
  });

  await fetch("/images")
    .then(async (result) => {
      if (result.ok) {
        return result.json();
      }
    })
    .then((images) => {
      images.forEach(addOption);
    });
};
