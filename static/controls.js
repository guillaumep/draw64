const addOption = ({ image_id }) => {
  const existingOption = document.getElementById(`image-${image_id}`);
  if (existingOption) {
    return;
  }

  const option = document.createElement("option");
  option.value = image_id;
  option.text = image_id;
  option.id = `image-${image_id}`;

  const select = document.getElementById("images");
  select.appendChild(option);
};

const updateUserCount = (userCount) => {
  document.getElementById("user-count").innerText = userCount;
};

const fetchImage = async () => {
  return await fetch("/images")
    .then(async (result) => {
      if (result.ok) {
        return result.json();
      }
    })
    .then((images) => {
      images.forEach(addOption);
    });
};

const initializeUserCount = async () => {
  return await fetch("/statistics")
    .then(async (result) => {
      if (result.ok) {
        return result.json();
      }
    })
    .then((stats) => updateUserCount(stats.user_count));
};

const initControls = async () => {
  const select = document.getElementById("images");

  select.onchange = (event) => {
    const imageId = event.target.value;
    loadImage(imageId);
    initWebSocket(imageId);
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

  evtSource.addEventListener("user_count_updated", (event) => {
    const { user_count } = JSON.parse(event.data).event;
    document.getElementById("user-count").innerText = user_count;
  });

  await fetchImage();
  await initializeUserCount();
};
