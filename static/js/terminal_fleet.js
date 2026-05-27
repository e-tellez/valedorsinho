/**
 * Terminal Fleet Manager – client-side logic.
 *
 * Fetches terminals from the local API proxy and renders them in the table.
 * Store names are resolved in a second call and patched into the DOM once ready.
 */

(function () {
  "use strict";

  // ---------------------------------------------------------------------------
  // DOM refs
  // ---------------------------------------------------------------------------
  const tbody         = document.getElementById("fleet-tbody");
  const tableWrap     = document.querySelector(".fleet-table-wrap");
  const emptyState    = document.getElementById("fleet-empty");
  const loadingState  = document.getElementById("fleet-loading");
  const statusBanner  = document.getElementById("fleet-status");
  const searchInput   = document.getElementById("search-input");
  const btnRefresh    = document.getElementById("btn-refresh");
  const pagination    = document.getElementById("fleet-pagination");
  const btnPrev       = document.getElementById("btn-prev");
  const btnNext       = document.getElementById("btn-next");
  const pageInfo      = document.getElementById("page-info");
  const reassignBar   = document.getElementById("reassign-bar");
  const reassignCount = document.getElementById("reassign-count");
  const reassignStore = document.getElementById("reassign-store");
  const btnReassign   = document.getElementById("btn-reassign");
  const btnDeselect   = document.getElementById("btn-deselect");
  const selectAllCb   = document.getElementById("select-all");

  // ---------------------------------------------------------------------------
  // State
  // ---------------------------------------------------------------------------
  let currentPage    = 1;
  const pageSize     = 20;
  let totalPages     = 1;
  let storeCache     = {};        // storeId → store object
  let searchTimer    = null;
  let selectedTerminals = {};     // terminalId → { merchantId }
  let currentTerminals  = [];     // terminals on the current page
  let allStores         = [];     // flat list of stores fetched for the dropdown

  // ---------------------------------------------------------------------------
  // Helpers
  // ---------------------------------------------------------------------------

  function showStatus(message, isError) {
    statusBanner.textContent = message;
    statusBanner.className = "fleet-status" + (isError ? " fleet-status-error" : " fleet-status-info");
    statusBanner.classList.remove("hidden");
  }

  function hideStatus() {
    statusBanner.classList.add("hidden");
  }

  function setLoading(on) {
    loadingState.classList.toggle("hidden", !on);
    tableWrap.classList.toggle("hidden", on);
    pagination.classList.toggle("hidden", on);
    emptyState.classList.add("hidden");
  }

  function formatDate(isoString) {
    if (!isoString) return "—";
    var date = new Date(isoString);
    return date.toLocaleDateString(undefined, { year: "numeric", month: "short", day: "numeric" })
      + " " + date.toLocaleTimeString(undefined, { hour: "2-digit", minute: "2-digit" });
  }

  function statusBadgeHTML(status) {
    var label = status || "unknown";
    var cls = "badge-status";
    switch (label.toLowerCase()) {
      case "boarded":     cls += " badge-boarded"; break;
      case "inventory":   cls += " badge-inventory"; break;
      case "reassigntomerchantinventory":
      case "reassigntostore":
        cls += " badge-reassign"; break;
      default:            cls += " badge-other"; break;
    }
    return '<span class="' + cls + '">' + label + "</span>";
  }

  // ---------------------------------------------------------------------------
  // Store name resolution
  // ---------------------------------------------------------------------------

  function resolveStoreNames(terminals) {
    // Collect unique merchantIds that have stores assigned
    var merchantIds = {};
    terminals.forEach(function (terminal) {
      var assignment = terminal.assignment || {};
      if (assignment.storeId && assignment.merchantId) {
        merchantIds[assignment.merchantId] = true;
      }
    });

    var ids = Object.keys(merchantIds);
    if (ids.length === 0) return;

    ids.forEach(function (merchantId) {
      if (storeCache["__fetched_" + merchantId]) return;
      storeCache["__fetched_" + merchantId] = true;

      fetch("/terminal-fleet/api/stores?merchantId=" + encodeURIComponent(merchantId))
        .then(function (response) { return response.json(); })
        .then(function (data) {
          var stores = data.data || [];
          stores.forEach(function (store) {
            storeCache[store.id] = store;
          });
          patchStoreNames();
        })
        .catch(function () { /* best-effort */ });
    });
  }

  function patchStoreNames() {
    var cells = document.querySelectorAll("[data-store-id]");
    cells.forEach(function (cell) {
      var storeId = cell.getAttribute("data-store-id");
      var store = storeCache[storeId];
      if (store) {
        var name = store.shopperStatement || store.description || store.reference || storeId;
        cell.textContent = name;
        cell.title = storeId;
      }
    });
  }

  // ---------------------------------------------------------------------------
  // Render
  // ---------------------------------------------------------------------------

  function renderTerminals(terminals) {
    tbody.innerHTML = "";

    if (!terminals || terminals.length === 0) {
      tableWrap.classList.add("hidden");
      emptyState.classList.remove("hidden");
      pagination.classList.add("hidden");
      return;
    }

    tableWrap.classList.remove("hidden");
    emptyState.classList.add("hidden");

    terminals.forEach(function (terminal) {
      var assignment = terminal.assignment || {};
      var terminalId = terminal.id || "";
      var isChecked = !!selectedTerminals[terminalId];
      var row = document.createElement("tr");
      if (isChecked) row.classList.add("row-selected");

      row.innerHTML =
        "<td class='col-checkbox'>" +
          "<input type='checkbox' class='terminal-checkbox' data-terminal-id='" + terminalId + "'" +
          " data-merchant-id='" + (assignment.merchantId || "") + "'" +
          (isChecked ? " checked" : "") + " />" +
        "</td>" +
        "<td class='col-id'>" + (terminalId || "—") + "</td>" +
        "<td>" + (terminal.model || "—") + "</td>" +
        "<td class='col-serial'>" + (terminal.serialNumber || "—") + "</td>" +
        "<td>" + statusBadgeHTML(assignment.status) + "</td>" +
        "<td data-store-id='" + (assignment.storeId || "") + "'>" +
          (assignment.storeId || "—") +
        "</td>" +
        "<td>" + (assignment.merchantId || "—") + "</td>" +
        "<td class='col-date'>" + formatDate(terminal.lastActivityAt) + "</td>";

      tbody.appendChild(row);
    });

    resolveStoreNames(terminals);
    syncSelectAll();
  }

  function updatePagination() {
    pageInfo.textContent = "Page " + currentPage + " of " + totalPages;
    btnPrev.disabled = currentPage <= 1;
    btnNext.disabled = currentPage >= totalPages;
    pagination.classList.toggle("hidden", totalPages <= 1);
  }

  // ---------------------------------------------------------------------------
  // Fetch
  // ---------------------------------------------------------------------------

  function fetchTerminals() {
    hideStatus();
    setLoading(true);

    var params = new URLSearchParams();
    params.set("pageNumber", currentPage);
    params.set("pageSize", pageSize);

    var query = searchInput.value.trim();
    if (query) params.set("searchQuery", query);

    fetch("/terminal-fleet/api/terminals?" + params.toString())
      .then(function (response) {
        if (!response.ok) {
          return response.json().catch(function () { return {}; }).then(function (body) {
            throw new Error(body.error || "HTTP " + response.status);
          });
        }
        return response.json();
      })
      .then(function (data) {
        setLoading(false);
        totalPages = data.pagesTotal || 1;
        currentTerminals = data.data || [];
        renderTerminals(currentTerminals);
        updatePagination();
      })
      .catch(function (err) {
        setLoading(false);
        tableWrap.classList.add("hidden");
        showStatus(err.message, true);
      });
  }

  // ---------------------------------------------------------------------------
  // Selection helpers
  // ---------------------------------------------------------------------------

  function updateReassignBar() {
    var ids = Object.keys(selectedTerminals);
    var count = ids.length;
    reassignCount.textContent = count + " selected";
    reassignBar.classList.toggle("hidden", count === 0);
    btnReassign.disabled = count === 0 || !reassignStore.value;

    if (count > 0 && allStores.length === 0) {
      fetchStoresForDropdown();
    }
  }

  function syncSelectAll() {
    var checkboxes = tbody.querySelectorAll(".terminal-checkbox");
    var allChecked = checkboxes.length > 0;
    checkboxes.forEach(function (cb) {
      if (!cb.checked) allChecked = false;
    });
    selectAllCb.checked = allChecked && checkboxes.length > 0;
  }

  function toggleTerminalSelection(terminalId, merchantId, selected) {
    if (selected) {
      selectedTerminals[terminalId] = { merchantId: merchantId };
    } else {
      delete selectedTerminals[terminalId];
    }
    updateReassignBar();
  }

  // ---------------------------------------------------------------------------
  // Store dropdown for reassignment
  // ---------------------------------------------------------------------------

  function fetchStoresForDropdown() {
    var merchantIds = {};
    Object.keys(selectedTerminals).forEach(function (terminalId) {
      merchantIds[selectedTerminals[terminalId].merchantId] = true;
    });

    Object.keys(merchantIds).forEach(function (merchantId) {
      if (!merchantId) return;
      fetch("/terminal-fleet/api/stores?merchantId=" + encodeURIComponent(merchantId))
        .then(function (response) { return response.json(); })
        .then(function (data) {
          var stores = data.data || [];
          stores.forEach(function (store) {
            if (!allStores.some(function (s) { return s.id === store.id; })) {
              allStores.push(store);
            }
          });
          populateStoreDropdown();
        })
        .catch(function () { /* best-effort */ });
    });
  }

  function populateStoreDropdown() {
    reassignStore.innerHTML = '<option value="">Select target store\u2026</option>';
    allStores.forEach(function (store) {
      var name = store.shopperStatement || store.description || store.reference || store.id;
      var option = document.createElement("option");
      option.value = store.id;
      option.textContent = name;
      option.title = store.id;
      reassignStore.appendChild(option);
    });
    reassignStore.disabled = allStores.length === 0;
  }

  // ---------------------------------------------------------------------------
  // Reassign action
  // ---------------------------------------------------------------------------

  function performReassign() {
    var storeId = reassignStore.value;
    if (!storeId) return;

    var ids = Object.keys(selectedTerminals);
    if (ids.length === 0) return;

    var merchantId = selectedTerminals[ids[0]].merchantId;

    btnReassign.disabled = true;
    btnReassign.textContent = "Reassigning\u2026";

    fetch("/terminal-fleet/api/reassign", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        terminalIds: ids,
        storeId: storeId,
        merchantId: merchantId,
      }),
    })
      .then(function (response) { return response.json(); })
      .then(function (data) {
        showStatus(data.summary || "Reassignment complete.", false);
        selectedTerminals = {};
        updateReassignBar();
        fetchTerminals();
      })
      .catch(function (err) {
        showStatus("Reassign failed: " + err.message, true);
      })
      .finally(function () {
        btnReassign.disabled = false;
        btnReassign.textContent = "Reassign";
      });
  }

  // ---------------------------------------------------------------------------
  // Events
  // ---------------------------------------------------------------------------

  btnRefresh.addEventListener("click", function () {
    currentPage = 1;
    fetchTerminals();
  });

  searchInput.addEventListener("input", function () {
    clearTimeout(searchTimer);
    searchTimer = setTimeout(function () {
      currentPage = 1;
      fetchTerminals();
    }, 400);
  });

  btnPrev.addEventListener("click", function () {
    if (currentPage > 1) { currentPage--; fetchTerminals(); }
  });

  btnNext.addEventListener("click", function () {
    if (currentPage < totalPages) { currentPage++; fetchTerminals(); }
  });

  tbody.addEventListener("change", function (e) {
    if (!e.target.classList.contains("terminal-checkbox")) return;
    var terminalId = e.target.getAttribute("data-terminal-id");
    var merchantId = e.target.getAttribute("data-merchant-id");
    toggleTerminalSelection(terminalId, merchantId, e.target.checked);
    e.target.closest("tr").classList.toggle("row-selected", e.target.checked);
    syncSelectAll();
  });

  selectAllCb.addEventListener("change", function () {
    var checked = selectAllCb.checked;
    var checkboxes = tbody.querySelectorAll(".terminal-checkbox");
    checkboxes.forEach(function (cb) {
      cb.checked = checked;
      var terminalId = cb.getAttribute("data-terminal-id");
      var merchantId = cb.getAttribute("data-merchant-id");
      toggleTerminalSelection(terminalId, merchantId, checked);
      cb.closest("tr").classList.toggle("row-selected", checked);
    });
  });

  reassignStore.addEventListener("change", function () {
    btnReassign.disabled = !reassignStore.value || Object.keys(selectedTerminals).length === 0;
  });

  btnReassign.addEventListener("click", performReassign);

  btnDeselect.addEventListener("click", function () {
    selectedTerminals = {};
    selectAllCb.checked = false;
    var checkboxes = tbody.querySelectorAll(".terminal-checkbox");
    checkboxes.forEach(function (cb) {
      cb.checked = false;
      cb.closest("tr").classList.remove("row-selected");
    });
    updateReassignBar();
  });

  // ---------------------------------------------------------------------------
  // Init
  // ---------------------------------------------------------------------------
  fetchTerminals();
})();
