/**
 * Terminal Payments – cascading terminal selector.
 *
 * Populates Company Account → Merchant Account → Store → Terminal
 * dropdowns from the Adyen Management API and gates the flow cards
 * until a terminal is selected.
 */

(function () {
  "use strict";

  // ---------------------------------------------------------------------------
  // DOM refs
  // ---------------------------------------------------------------------------
  var companyField    = document.getElementById("company-account");
  var merchantSelect  = document.getElementById("merchant-select");
  var storeSelect     = document.getElementById("store-select");
  var terminalSelect  = document.getElementById("terminal-select");
  var flowsSection    = document.getElementById("flows-section");
  var flowsHint       = document.getElementById("flows-hint");
  var flowLinks       = document.querySelectorAll(".flow-link");
  var statusBanner    = document.getElementById("tp-status");
  var selectedInfo    = document.getElementById("selected-info");

  // ---------------------------------------------------------------------------
  // State
  // ---------------------------------------------------------------------------
  var selectedTerminalId     = "";
  var selectedMerchantAccount = "";

  // ---------------------------------------------------------------------------
  // Helpers
  // ---------------------------------------------------------------------------

  function showStatus(message, isError) {
    statusBanner.textContent = message;
    statusBanner.className = "tp-status" + (isError ? " tp-status-error" : " tp-status-info");
    statusBanner.classList.remove("hidden");
  }

  function hideStatus() {
    statusBanner.classList.add("hidden");
  }

  function setSelectLoading(selectElement) {
    selectElement.disabled = true;
    selectElement.innerHTML = '<option value="">Loading\u2026</option>';
  }

  function resetSelect(selectElement, placeholder) {
    selectElement.innerHTML = '<option value="">' + placeholder + "</option>";
    selectElement.disabled = true;
  }

  function enableFlows(enabled) {
    if (enabled) {
      flowsSection.classList.remove("flows-disabled");
      flowsHint.classList.add("hidden");
    } else {
      flowsSection.classList.add("flows-disabled");
      flowsHint.classList.remove("hidden");
    }
  }

  function updateFlowLinks() {
    flowLinks.forEach(function (link) {
      var baseHref = link.getAttribute("data-base-href");
      if (selectedTerminalId) {
        link.href = baseHref +
          "?terminalId=" + encodeURIComponent(selectedTerminalId) +
          "&merchantAccount=" + encodeURIComponent(selectedMerchantAccount);
      } else {
        link.href = "#";
      }
    });
  }

  // ---------------------------------------------------------------------------
  // Fetch merchants
  // ---------------------------------------------------------------------------

  function fetchMerchants() {
    setSelectLoading(merchantSelect);
    resetSelect(storeSelect, "Select a merchant first");
    resetSelect(terminalSelect, "Select a merchant first");

    fetch("/terminal-payments/api/merchants")
      .then(function (response) {
        if (!response.ok) {
          return response.json().catch(function () { return {}; }).then(function (body) {
            throw new Error(body.error || "HTTP " + response.status);
          });
        }
        return response.json();
      })
      .then(function (data) {
        var merchants = data.data || [];
        merchantSelect.innerHTML = '<option value="">Select merchant account\u2026</option>';

        merchants.forEach(function (merchant) {
          var option = document.createElement("option");
          option.value = merchant.id;
          option.textContent = merchant.id;
          if (merchant.name) {
            option.textContent = merchant.id + " (" + merchant.name + ")";
          }
          merchantSelect.appendChild(option);
        });

        merchantSelect.disabled = merchants.length === 0;

        // Display company account from the first merchant's companyId
        if (merchants.length > 0 && merchants[0].companyId) {
          companyField.textContent = merchants[0].companyId;
        } else {
          companyField.textContent = "\u2014";
        }

        // Auto-select if only one merchant
        if (merchants.length === 1) {
          merchantSelect.value = merchants[0].id;
          merchantSelect.dispatchEvent(new Event("change"));
        }

        if (merchants.length === 0) {
          merchantSelect.innerHTML = '<option value="">No merchants found</option>';
        }
      })
      .catch(function (err) {
        merchantSelect.innerHTML = '<option value="">Error loading merchants</option>';
        companyField.textContent = "\u2014";
        showStatus("Failed to load merchants: " + err.message, true);
      });
  }

  // ---------------------------------------------------------------------------
  // Fetch stores for selected merchant
  // ---------------------------------------------------------------------------

  function fetchStores(merchantId) {
    setSelectLoading(storeSelect);

    fetch("/terminal-payments/api/stores?merchantId=" + encodeURIComponent(merchantId))
      .then(function (response) {
        if (!response.ok) {
          return response.json().catch(function () { return {}; }).then(function (body) {
            throw new Error(body.error || "HTTP " + response.status);
          });
        }
        return response.json();
      })
      .then(function (data) {
        var stores = data.data || [];
        storeSelect.innerHTML = '<option value="">All stores</option>';

        stores.forEach(function (store) {
          var option = document.createElement("option");
          option.value = store.id;
          var name = store.description || store.shopperStatement || store.reference || store.id;
          option.textContent = name;
          option.title = store.id;
          storeSelect.appendChild(option);
        });

        storeSelect.disabled = false;
      })
      .catch(function (err) {
        storeSelect.innerHTML = '<option value="">Error loading stores</option>';
        showStatus("Failed to load stores: " + err.message, true);
      });
  }

  // ---------------------------------------------------------------------------
  // Fetch terminals for selected merchant (+ optional store filter)
  // ---------------------------------------------------------------------------

  function fetchTerminals(merchantId, storeId) {
    setSelectLoading(terminalSelect);

    // Clear current selection
    selectedTerminalId = "";
    selectedMerchantAccount = "";
    enableFlows(false);
    updateFlowLinks();
    selectedInfo.classList.add("hidden");

    var params = new URLSearchParams();
    params.set("merchantIds", merchantId);
    if (storeId) {
      params.set("storeIds", storeId);
    }
    params.set("pageSize", "100");

    fetch("/terminal-payments/api/terminals?" + params.toString())
      .then(function (response) {
        if (!response.ok) {
          return response.json().catch(function () { return {}; }).then(function (body) {
            throw new Error(body.error || "HTTP " + response.status);
          });
        }
        return response.json();
      })
      .then(function (data) {
        var terminals = data.data || [];
        terminalSelect.innerHTML = '<option value="">Select terminal\u2026</option>';

        terminals.forEach(function (terminal) {
          var option = document.createElement("option");
          option.value = terminal.id;
          var label = terminal.id;
          if (terminal.model) {
            label += " \u2013 " + terminal.model;
          }
          option.textContent = label;
          terminalSelect.appendChild(option);
        });

        terminalSelect.disabled = terminals.length === 0;

        if (terminals.length === 0) {
          terminalSelect.innerHTML = '<option value="">No terminals found</option>';
        }
      })
      .catch(function (err) {
        terminalSelect.innerHTML = '<option value="">Error loading terminals</option>';
        showStatus("Failed to load terminals: " + err.message, true);
      });
  }

  // ---------------------------------------------------------------------------
  // Event handlers
  // ---------------------------------------------------------------------------

  merchantSelect.addEventListener("change", function () {
    hideStatus();
    var merchantId = merchantSelect.value;

    if (!merchantId) {
      resetSelect(storeSelect, "Select a merchant first");
      resetSelect(terminalSelect, "Select a merchant first");
      selectedTerminalId = "";
      selectedMerchantAccount = "";
      enableFlows(false);
      updateFlowLinks();
      selectedInfo.classList.add("hidden");
      return;
    }

    fetchStores(merchantId);
    fetchTerminals(merchantId, "");
  });

  storeSelect.addEventListener("change", function () {
    hideStatus();
    var merchantId = merchantSelect.value;
    var storeId = storeSelect.value;
    if (merchantId) {
      fetchTerminals(merchantId, storeId);
    }
  });

  terminalSelect.addEventListener("change", function () {
    hideStatus();
    selectedTerminalId = terminalSelect.value;
    selectedMerchantAccount = merchantSelect.value;

    if (selectedTerminalId) {
      enableFlows(true);
      selectedInfo.textContent = "\u2713 Selected: " + selectedTerminalId;
      selectedInfo.classList.remove("hidden");
    } else {
      enableFlows(false);
      selectedInfo.classList.add("hidden");
    }

    updateFlowLinks();
  });

  // ---------------------------------------------------------------------------
  // Init
  // ---------------------------------------------------------------------------
  fetchMerchants();
})();
