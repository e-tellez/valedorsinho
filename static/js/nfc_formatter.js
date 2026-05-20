(() => {
  const keyAInput      = document.getElementById("key-a");
  const keyBInput      = document.getElementById("key-b");
  const keyAError      = document.getElementById("key-a-error");
  const keyBError      = document.getElementById("key-b-error");
  const bgCheckbox     = document.getElementById("do-in-background");
  const preview        = document.getElementById("payload-preview");
  const btnCopy        = document.getElementById("btn-copy");
  const btnDownload    = document.getElementById("btn-download");
  const banner         = document.getElementById("copy-banner");

  const HEX_REGEX = /^[0-9a-fA-F]{12}$/;

  function buildPayload() {
    const keyA = keyAInput.value.trim() || "***";
    const keyB = keyBInput.value.trim() || "***";
    const doInBackground = bgCheckbox.checked;

    return {
      cardAcquisition: [
        {
          conf: [
            {
              keys: [
                { key: keyA, keyType: "a" },
                { key: keyB, keyType: "b" },
              ],
              sector: 2,
            },
          ],
          convert: { dataType: "hex", length: 0, offset: 0 },
          ref: "mifareClassicCard",
        },
        {
          convert: { dataType: "hex", length: 0, offset: 0 },
          length: 256,
          offset: 0,
          ref: "type2Card",
        },
      ],
      doInBackground: doInBackground,
    };
  }

  function validateKey(input, errorSpan) {
    const value = input.value.trim();
    if (value === "" || HEX_REGEX.test(value)) {
      errorSpan.classList.add("hidden");
      return true;
    }
    errorSpan.classList.remove("hidden");
    return false;
  }

  function updatePreview() {
    validateKey(keyAInput, keyAError);
    validateKey(keyBInput, keyBError);
    const payload = buildPayload();
    preview.textContent = JSON.stringify(payload, null, 2);
  }

  // Initial render
  updatePreview();

  // Live update on input
  keyAInput.addEventListener("input", updatePreview);
  keyBInput.addEventListener("input", updatePreview);
  bgCheckbox.addEventListener("change", updatePreview);

  // Copy to clipboard
  btnCopy.addEventListener("click", async () => {
    const text = JSON.stringify(buildPayload(), null, 2);
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
  btnDownload.addEventListener("click", () => {
    const text = JSON.stringify(buildPayload(), null, 2);
    const blob = new Blob([text], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "nfc_card_acquisition.json";
    link.click();
    URL.revokeObjectURL(url);
  });

  function showBanner() {
    banner.classList.remove("hidden");
    setTimeout(() => banner.classList.add("hidden"), 2000);
  }
})();
