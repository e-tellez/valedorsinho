(() => {
  const preview    = document.getElementById("payload-preview");
  const btnCopy    = document.getElementById("btn-copy");
  const btnDown    = document.getElementById("btn-download");
  const banner     = document.getElementById("copy-banner");
  const checkboxes = document.querySelectorAll('input[name="vertical"]');

  let currentPayload = {};

  function deepMerge(target, source) {
    const result = { ...target };
    for (const key of Object.keys(source)) {
      if (
        result[key] && typeof result[key] === "object" && !Array.isArray(result[key]) &&
        typeof source[key] === "object" && !Array.isArray(source[key])
      ) {
        result[key] = deepMerge(result[key], source[key]);
      } else {
        result[key] = source[key];
      }
    }
    return result;
  }

  function updatePreview() {
    const selected = document.querySelectorAll('input[name="vertical"]:checked');
    if (selected.length === 0) {
      currentPayload = {};
      preview.textContent = "Select at least one vertical.";
      return;
    }

    let merged = {};
    selected.forEach((checkbox) => {
      const payload = JSON.parse(checkbox.dataset.payload);
      merged = deepMerge(merged, payload);
    });
    currentPayload = merged;
    preview.textContent = JSON.stringify(currentPayload, null, 2);
  }

  // Initial render
  updatePreview();

  // Change on checkbox toggle
  checkboxes.forEach((checkbox) => {
    checkbox.addEventListener("change", updatePreview);
  });

  // Copy to clipboard
  btnCopy.addEventListener("click", async () => {
    const text = JSON.stringify(currentPayload, null, 2);
    try {
      await navigator.clipboard.writeText(text);
      showBanner();
    } catch (err) {
      const textarea = document.createElement("textarea");
      textarea.value = text;
      document.body.appendChild(textarea);
      textarea.select();
      document.execCommand("copy");
      document.body.removeChild(textarea);
      showBanner();
    }
  });

  // Download .json
  btnDown.addEventListener("click", () => {
    const text = JSON.stringify(currentPayload, null, 2);
    const selected = document.querySelectorAll('input[name="vertical"]:checked');
    const keys = Array.from(selected).map((c) => c.value).join("_");
    const blob = new Blob([text], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `payload_${keys || "empty"}.json`;
    link.click();
    URL.revokeObjectURL(url);
  });

  // Show/hide banner
  function showBanner() {
    banner.classList.remove("hidden");
    setTimeout(() => banner.classList.add("hidden"), 2000);
  }
})();
