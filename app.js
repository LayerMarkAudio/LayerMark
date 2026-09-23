const players = Array.from(document.querySelectorAll("audio"));

const formatTime = (seconds) => {
  if (!Number.isFinite(seconds)) return "--:--";
  return `${Math.floor(seconds / 60)}:${String(Math.floor(seconds % 60)).padStart(2, "0")}`;
};

const setIcon = (button, name) => {
  if (window.lucide) {
    button.replaceChildren(lucide.createElement(lucide.icons[name], { "aria-hidden": "true" }));
  } else {
    button.textContent = name === "Pause" ? "\u2161" : "\u25b6";
  }
};

// Enhance the sample controls with the same player used in the comparison.
for (const audio of document.querySelectorAll(".audio-table audio")) {
  const row = audio.closest(".audio-row");
  const sample = row.querySelector(".sample-label strong").textContent;
  const cells = Array.from(row.querySelectorAll('[role="cell"]'));
  const layer = cells.indexOf(audio.parentElement);
  const label = layer === 0 ? "Original audio" : `Layer ${layer}`;
  const wrapper = document.createElement("div");
  wrapper.className = "mini-player";
  wrapper.dataset.layer = `L${layer}`;
  const button = document.createElement("button");
  button.type = "button";
  button.setAttribute("aria-label", `Play ${sample} ${label.toLowerCase()}`);
  const detail = document.createElement("div");
  const title = document.createElement("span");
  title.textContent = label;
  const track = document.createElement("div");
  track.className = "player-track";
  detail.append(title, track);
  wrapper.append(button, detail, document.createElement("time"));
  audio.before(wrapper);
  wrapper.append(audio);
  audio.controls = false;
}

for (const player of players) {
  player.addEventListener("play", () => {
    for (const other of players) {
      if (other !== player && !other.paused) other.pause();
    }
  });
}

for (const wrapper of document.querySelectorAll(".mini-player")) {
  const audio = wrapper.querySelector("audio");
  const button = wrapper.querySelector("button");
  const time = wrapper.querySelector("time");
  const description = button.getAttribute("aria-label").replace(/^Play /, "");
  const track = wrapper.querySelector(".player-track");
  const seek = document.createElement("input");
  seek.type = "range";
  seek.min = "0";
  seek.max = "100";
  seek.step = "0.1";
  seek.value = "0";
  seek.disabled = true;
  seek.setAttribute("aria-label", `Seek ${description}`);
  track.replaceChildren(seek);
  time.setAttribute("aria-live", "off");
  wrapper.setAttribute("role", "group");
  wrapper.setAttribute("aria-label", description);
  if (wrapper.closest(".comparison-row")) wrapper.setAttribute("role", "cell");

  const update = () => {
    const hasDuration = Number.isFinite(audio.duration) && audio.duration > 0;
    const progress = hasDuration ? audio.currentTime / audio.duration * 100 : 0;
    seek.disabled = !hasDuration;
    seek.value = String(progress);
    seek.style.setProperty("--progress", `${progress}%`);
    seek.setAttribute("aria-valuetext", `${formatTime(audio.currentTime)} of ${formatTime(audio.duration)}`);
    time.textContent = `${formatTime(audio.currentTime)} / ${formatTime(audio.duration)}`;
  };
  const updateState = () => {
    const playing = !audio.paused && !audio.ended;
    wrapper.classList.toggle("is-playing", playing);
    button.setAttribute("aria-label", `${playing ? "Pause" : "Play"} ${description}`);
    button.title = button.getAttribute("aria-label");
    setIcon(button, playing ? "Pause" : "Play");
  };
  const showError = () => {
    time.textContent = "Audio unavailable";
    time.classList.add("player-error");
    updateState();
  };
  update();
  updateState();
  audio.addEventListener("loadedmetadata", update);
  audio.addEventListener("timeupdate", update);
  audio.addEventListener("play", updateState);
  audio.addEventListener("pause", updateState);
  audio.addEventListener("ended", () => { update(); updateState(); });
  audio.addEventListener("error", showError);
  if (audio.error) showError();

  seek.addEventListener("input", () => {
    if (Number.isFinite(audio.duration)) {
      audio.currentTime = Number(seek.value) / 100 * audio.duration;
      update();
    }
  });
  button.addEventListener("click", async () => {
    if (!audio.paused) {
      audio.pause();
      return;
    }
    if (audio.ended) audio.currentTime = 0;
    try {
      await audio.play();
      time.classList.remove("player-error");
    } catch (error) {
      if (error.name !== "AbortError") showError();
    }
  });
}
if (window.lucide) lucide.createIcons();
