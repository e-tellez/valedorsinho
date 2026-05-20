(() => {
  const input       = document.getElementById("payload-input");
  const btnValidate = document.getElementById("btn-validate");
  const btnExport   = document.getElementById("btn-export-csv");
  const banner      = document.getElementById("status-banner");
  const errorsSection = document.getElementById("errors-section");
  const errorsBody  = document.getElementById("errors-body");

  let lastErrors = [];

  // -- Validate --------------------------------------------------------- //

  btnValidate.addEventListener("click", async () => {
    const raw = input.value.trim();
    if (!raw) {
      showBanner("error", "Please paste a JSON payload first.");
      return;
    }

    let payload;
    try {
      payload = JSON.parse(raw);
    } catch (e) {
      showBanner("error", "Invalid JSON: " + e.message);
      return;
    }

    showBanner("loading", "Validating against OpenAPI spec\u2026");
    btnValidate.disabled = true;

    try {
      const res = await fetch("/api/validate-payload", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ payload }),
      });
      const data = await res.json();

      if (!res.ok) {
        showBanner("error", data.error || "Server error.");
        hideErrors();
        return;
      }

      lastErrors = data.errors || [];

      if (data.valid) {
        showBanner("success", "Payload is valid \u2014 no errors found.");
        hideErrors();
        btnExport.disabled = true;
      } else {
        showBanner("error", lastErrors.length + " validation error(s) found.");
        renderErrors(lastErrors);
        btnExport.disabled = false;
      }
    } catch (err) {
      showBanner("error", "Network error: " + err.message);
      hideErrors();
    } finally {
      btnValidate.disabled = false;
    }
  });

  // -- Export CSV -------------------------------------------------------- //

  btnExport.addEventListener("click", () => {
    if (!lastErrors.length) return;

    const header = "Field,Error,Rule";
    const rows = lastErrors.map(
      (e) => `"${esc(e.field)}","${esc(e.error)}","${esc(e.rule)}"`
    );
    const csv = [header, ...rows].join("\n");
    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = "payload_validation_errors.csv";
    link.click();
    URL.revokeObjectURL(url);
  });

  // -- Helpers ---------------------------------------------------------- //

  function esc(str) {
    return String(str).replace(/"/g, '""');
  }

  function showBanner(type, message) {
    banner.className = "status-banner " + type;
    banner.textContent = message;
  }

  function renderErrors(errors) {
    errorsBody.innerHTML = "";
    errors.forEach((e) => {
      const tr = document.createElement("tr");
      tr.innerHTML =
        `<td>${escHtml(e.field)}</td>` +
        `<td>${escHtml(e.error)}</td>` +
        `<td>${escHtml(e.rule)}</td>`;
      errorsBody.appendChild(tr);
    });
    errorsSection.classList.remove("hidden");
  }

  function hideErrors() {
    errorsSection.classList.add("hidden");
    errorsBody.innerHTML = "";
  }

  function escHtml(str) {
    const div = document.createElement("div");
    div.textContent = String(str);
    return div.innerHTML;
  }
})();
