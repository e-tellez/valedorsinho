(() => {
  const preview   = document.getElementById("payload-preview");
  const btnCopy   = document.getElementById("btn-copy");
  const btnDown   = document.getElementById("btn-download");
  const banner    = document.getElementById("copy-banner");
  const radios    = document.querySelectorAll('input[name="vertical"]');

  let currentPayload = {};

  function updatePreview() {
    const selected = document.querySelector('input[name="vertical"]:checked');
    if (!selected) return;
    currentPayload = JSON.parse(selected.dataset.payload);
    preview.textContent = JSON.stringify(currentPayload, null, 2);
  }

  // Initial render
  updatePreview();

  // Change on radio select
  radios.forEach((radio) => {
    radio.addEventListener("change", updatePreview);
  });

  // Copy to clipboard
  btnCopy.addEventListener("click", async () => {
    const text = JSON.stringify(currentPayload, null, 2);
    try {
      await navigator.clipboard.writeText(text);
      showBanner();
    } catch (err) {
      // Fallback for older browsers
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
    const selected = document.querySelector('input[name="vertical"]:checked');
    const key = selected ? selected.value : "payload";
    const blob = new Blob([text], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = `payload_${key}.json`;
    link.click();
    URL.revokeObjectURL(url);
  });

  // Show/hide banner
  function showBanner() {
    banner.classList.remove("hidden");
    setTimeout(() => banner.classList.add("hidden"), 2000);
  }
})();
