/* ------------------------------------------------------------------ */
/* Terminal – Make a Payment: live payload builder                      */
/* ------------------------------------------------------------------ */
(function () {
  "use strict";

  /* ---- DOM refs -------------------------------------------------- */
  const amountInput        = document.getElementById("mp-amount");
  const currencyInput      = document.getElementById("mp-currency");
  const askGratuityToggle  = document.getElementById("mp-ask-gratuity");
  const receiptToggle      = document.getElementById("mp-receipt-handler");
  const forceEntryRadios   = document.querySelectorAll('input[name="forceEntryMode"]');
  const shopperRefInput    = document.getElementById("mp-shopper-reference");
  const recurringSelect    = document.getElementById("mp-recurring-contract");
  const authTypeSelect     = document.getElementById("mp-authorisation-type");
  const shopperEmailInput  = document.getElementById("mp-shopper-email");
  const storeInput         = document.getElementById("mp-store");
  const metadataList       = document.getElementById("mp-metadata-list");
  const addMetadataBtn     = document.getElementById("mp-add-metadata");
  const payloadPre         = document.getElementById("mp-payload-json");
  const acquirerPre        = document.getElementById("mp-acquirer-json");
  const copyBtn            = document.getElementById("mp-copy-btn");
  const sendBtn            = document.getElementById("mp-send-btn");

  /* ---- Read terminal + merchant from query params ---------------- */
  const params          = new URLSearchParams(window.location.search);
  const terminalId      = params.get("terminalId") || "";
  const merchantAccount = params.get("merchantAccount") || "";

  const terminalSpan  = document.getElementById("mp-terminal-id");
  const merchantSpan  = document.getElementById("mp-merchant-id");
  if (terminalSpan)  terminalSpan.textContent = terminalId || "—";
  if (merchantSpan)  merchantSpan.textContent = merchantAccount || "—";

  /* ---- Helpers --------------------------------------------------- */
  function generateServiceId() {
    return String(Math.floor(Math.random() * 10000000000));
  }

  function generateTransactionId() {
    return "ipp-" + Date.now().toString(36) + Math.random().toString(36).substring(2, 6);
  }

  /* Generate once per page load */
  var serviceId     = generateServiceId();
  var transactionId = generateTransactionId();

  function getForceEntryMode() {
    for (const radio of forceEntryRadios) {
      if (radio.checked) return radio.value;
    }
    return "";
  }

  function getMetadata() {
    const rows = metadataList.querySelectorAll(".mp-kv-row");
    const meta = {};
    rows.forEach(function (row) {
      const inputs = row.querySelectorAll("input");
      const key   = inputs[0].value.trim();
      const value = inputs[1].value.trim();
      if (key) meta[key] = value;
    });
    return Object.keys(meta).length ? meta : null;
  }

  /* ---- Build SaleToAcquirerData object --------------------------- */
  function buildAcquirerData() {
    const data = {};

    /* Tender options */
    const tenderOptions = [];
    if (askGratuityToggle.checked)  tenderOptions.push("AskGratuity");
    if (receiptToggle.checked)      tenderOptions.push("ReceiptHandler");
    if (tenderOptions.length) data.tenderOption = tenderOptions.join(",");

    /* SaleToAcquirerData fields */
    const shopperRef = shopperRefInput.value.trim();
    if (shopperRef) data.shopperReference = shopperRef;

    const recurring = recurringSelect.value;
    if (recurring) data.recurringContract = recurring;

    const authType = authTypeSelect.value;
    if (authType) data.authorisationType = authType;

    const email = shopperEmailInput.value.trim();
    if (email && email.indexOf("@") !== -1) data.shopperEmail = email;

    const store = storeInput.value.trim();
    if (store) data.store = store;

    const metadata = getMetadata();
    if (metadata) data.metadata = metadata;

    return Object.keys(data).length ? data : null;
  }

  /* ---- Build full payload ---------------------------------------- */
  function buildPayload() {
    const amount   = parseFloat(amountInput.value) || 0;
    const currency = currencyInput.value.trim() || "EUR";

    const acquirerData = buildAcquirerData();
    const acquirerB64  = acquirerData
      ? btoa(JSON.stringify(acquirerData))
      : null;

    const payload = {
      SaleToPOIRequest: {
        MessageHeader: {
          ProtocolVersion: "3.0",
          MessageClass: "Service",
          MessageCategory: "Payment",
          MessageType: "Request",
          ServiceID: serviceId,
          SaleID: "Valedorsinho",
          POIID: terminalId || "<terminalId>"
        },
        PaymentRequest: {
          SaleData: {
            SaleTransactionID: {
              TransactionID: transactionId,
              TimeStamp: new Date().toISOString()
            }
          },
          PaymentTransaction: {
            AmountsReq: {
              Currency: currency,
              RequestedAmount: amount
            }
          },
          PaymentData: {
            PaymentType: "Normal"
          }
        }
      }
    };

    /* Attach SaleToAcquirerData */
    if (acquirerB64) {
      payload.SaleToPOIRequest.PaymentRequest.SaleData.SaleToAcquirerData = acquirerB64;
    }

    /* Attach ForceEntryMode */
    const forceEntry = getForceEntryMode();
    if (forceEntry) {
      payload.SaleToPOIRequest.PaymentRequest.PaymentTransaction.TransactionConditions = {
        ForceEntryMode: [forceEntry]
      };
    }

    return { payload: payload, acquirerData: acquirerData };
  }

  /* ---- JSON syntax highlighting ---------------------------------- */
  function syntaxHighlight(json) {
    var str = JSON.stringify(json, null, 2);
    str = str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
    return str.replace(
      /("(\\u[\da-fA-F]{4}|\\[^u]|[^\\"])*"(\s*:)?|\b(true|false)\b|-?\d+(?:\.\d*)?(?:[eE][+\-]?\d+)?|\bnull\b)/g,
      function (match) {
        var cls = "json-number";
        if (/^"/.test(match)) {
          if (/:$/.test(match)) {
            cls = "json-key";
            match = match.replace(/:$/, "") + ":";
          } else {
            cls = "json-string";
          }
        } else if (/true|false/.test(match)) {
          cls = "json-bool";
        } else if (/null/.test(match)) {
          cls = "json-null";
        }
        return '<span class="' + cls + '">' + match + "</span>";
      }
    );
  }

  /* ---- Email validation ------------------------------------------ */
  function isEmailValid() {
    var email = shopperEmailInput.value.trim();
    if (!email) return true; /* empty is fine – field is optional */
    return email.indexOf("@") !== -1;
  }

  function updateEmailVisual() {
    if (isEmailValid()) {
      shopperEmailInput.style.borderColor = "";
    } else {
      shopperEmailInput.style.borderColor = "#e53e3e";
    }
  }

  /* ---- Form validation ------------------------------------------- */
  function validateForm() {
    var amount = parseFloat(amountInput.value);
    var valid  = terminalId && amount > 0 && isEmailValid();
    sendBtn.disabled = !valid;
  }

  /* ---- Render preview -------------------------------------------- */
  function renderPreview() {
    updateEmailVisual();
    validateForm();
    var result       = buildPayload();
    payloadPre.innerHTML  = syntaxHighlight(result.payload);
    if (result.acquirerData) {
      acquirerPre.innerHTML = syntaxHighlight(result.acquirerData);
      acquirerPre.parentElement.style.display = "";
    } else {
      acquirerPre.innerHTML = "";
      acquirerPre.parentElement.style.display = "none";
    }
  }

  /* ---- Event listeners ------------------------------------------- */
  var allInputs = [
    amountInput, shopperRefInput,
    shopperEmailInput
  ];
  allInputs.forEach(function (el) {
    el.addEventListener("input", renderPreview);
  });

  var allSelects = [currencyInput, recurringSelect, authTypeSelect, storeInput];
  allSelects.forEach(function (el) {
    el.addEventListener("change", renderPreview);
  });

  var allToggles = [askGratuityToggle, receiptToggle];
  allToggles.forEach(function (el) {
    el.addEventListener("change", renderPreview);
  });

  forceEntryRadios.forEach(function (radio) {
    radio.addEventListener("change", renderPreview);
  });

  /* ---- Metadata rows --------------------------------------------- */
  function createMetadataRow(key, value) {
    var row = document.createElement("div");
    row.className = "mp-kv-row";
    row.innerHTML =
      '<input type="text" placeholder="key" value="' + (key || "") + '" />' +
      '<input type="text" placeholder="value" value="' + (value || "") + '" />' +
      '<button type="button" class="mp-kv-remove" title="Remove">&times;</button>';
    row.querySelectorAll("input").forEach(function (inp) {
      inp.addEventListener("input", renderPreview);
    });
    row.querySelector(".mp-kv-remove").addEventListener("click", function () {
      row.remove();
      renderPreview();
    });
    return row;
  }

  addMetadataBtn.addEventListener("click", function () {
    metadataList.appendChild(createMetadataRow());
    renderPreview();
  });

  /* ---- Send payment request -------------------------------------- */
  sendBtn.addEventListener("click", function () {
    var result = buildPayload();

    sendBtn.disabled = true;
    sendBtn.textContent = "Sending…";

    fetch("/terminal-payments/api/make-payment", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(result.payload)
    })
      .then(function (response) {
        return response.json().then(function (body) {
          return { status: response.status, body: body };
        });
      })
      .then(function (res) {
        /* POST response directly to the result page via hidden form */
        var resultUrl = "/terminal-payments/payment-result"
          + "?terminalId=" + encodeURIComponent(terminalId)
          + "&merchantAccount=" + encodeURIComponent(merchantAccount);
        var form = document.createElement("form");
        form.method = "POST";
        form.action = resultUrl;
        var input = document.createElement("input");
        input.type = "hidden";
        input.name = "response_data";
        input.value = JSON.stringify(res.body);
        form.appendChild(input);
        document.body.appendChild(form);
        form.submit();
      })
      .catch(function (err) {
        sendBtn.disabled = false;
        sendBtn.textContent = "Send Payment Request";
        alert("Request failed: " + err.message);
      });
  });

  /* ---- Copy payload ---------------------------------------------- */
  copyBtn.addEventListener("click", function () {
    var result = buildPayload();
    var text   = JSON.stringify(result.payload, null, 2);
    navigator.clipboard.writeText(text).then(function () {
      var orig = copyBtn.textContent;
      copyBtn.textContent = "Copied!";
      setTimeout(function () { copyBtn.textContent = orig; }, 1500);
    });
  });

  /* ---- Fetch stores for dropdown --------------------------------- */
  function loadStores() {
    if (!merchantAccount) return;
    fetch("/terminal-payments/api/stores?merchantId=" + encodeURIComponent(merchantAccount))
      .then(function (response) { return response.json(); })
      .then(function (data) {
        var stores = data.data || data.stores || [];
        stores.forEach(function (store) {
          var option = document.createElement("option");
          option.value = store.reference || "";
          option.textContent = (store.reference || "") + (store.description ? " – " + store.description : "");
          storeInput.appendChild(option);
        });
      })
      .catch(function (err) {
        console.error("Failed to load stores:", err);
      });
  }

  loadStores();

  /* ---- Initial render -------------------------------------------- */
  renderPreview();
})();
