document.addEventListener("DOMContentLoaded", () => {
  // ==================================================
  // ELEMENTS
  // ==================================================

  const unitSearch = document.getElementById("unitSearch");
  const searchResults = document.getElementById("unitSearchResults");
  const selectedUnitsInput = document.getElementById("selectedUnits");
  const selectedUnitsCard = document.getElementById("selectedUnitsCard");
  const selectedUnitsList = document.getElementById("selectedUnitsList");
  const deploymentForm = document.getElementById("deploymentForm");

  if (
    !unitSearch ||
    !searchResults ||
    !selectedUnitsInput ||
    !selectedUnitsCard ||
    !selectedUnitsList ||
    !deploymentForm
  ) {
    console.error("Deployment page elements were not found.");
    return;
  }

  const selectedUnits = [];
  let searchTimer = null;
  let activeRequest = null;

  // ==================================================
  // HELPERS
  // ==================================================

  function escapeHtml(value) {
    return String(value ?? "")
      .replaceAll("&", "&amp;")
      .replaceAll("<", "&lt;")
      .replaceAll(">", "&gt;")
      .replaceAll('"', "&quot;")
      .replaceAll("'", "&#039;");
  }

  function syncSelectedUnitsInput() {
    // Only IDs are needed by Flask. Example: [4, 7, 12]
    selectedUnitsInput.value = JSON.stringify(
      selectedUnits.map((unit) => Number(unit.id))
    );
  }

  function hideSearchResults() {
    searchResults.innerHTML = "";
    searchResults.hidden = true;
  }

  function renderSelectedUnits() {
    selectedUnitsList.innerHTML = "";

    if (selectedUnits.length === 0) {
      selectedUnitsCard.hidden = true;
      syncSelectedUnitsInput();
      return;
    }

    selectedUnitsCard.hidden = false;

    selectedUnits.forEach((unit) => {
      const row = document.createElement("div");
      row.className = "selected-unit-row";

      const info = document.createElement("div");
      info.className = "selected-unit-info";
      info.innerHTML = `
        <strong>${escapeHtml(unit.asset_code || "No Asset Code")}</strong>
        <br>
        ${escapeHtml(unit.brand || "")} ${escapeHtml(unit.model || "")}
        <br>
        <small>${escapeHtml(unit.serial_number || "No Serial Number")}</small>
      `;

      const removeButton = document.createElement("button");
      removeButton.type = "button";
      removeButton.className = "btn-danger btn-sm";
      removeButton.textContent = "Remove";
      removeButton.addEventListener("click", () => {
        removeSelectedUnit(unit.id);
      });

      row.appendChild(info);
      row.appendChild(removeButton);
      selectedUnitsList.appendChild(row);
    });

    syncSelectedUnitsInput();
  }

  function selectUnit(unit) {
    const alreadySelected = selectedUnits.some(
      (selected) => Number(selected.id) === Number(unit.id)
    );

    if (alreadySelected) {
      return;
    }

    selectedUnits.push(unit);
    renderSelectedUnits();

    unitSearch.value = "";
    hideSearchResults();
    unitSearch.focus();
  }

  function removeSelectedUnit(unitId) {
    const index = selectedUnits.findIndex(
      (unit) => Number(unit.id) === Number(unitId)
    );

    if (index !== -1) {
      selectedUnits.splice(index, 1);
    }

    renderSelectedUnits();
    hideSearchResults();
    unitSearch.value = "";
  }

  // ==================================================
  // SEARCH AVAILABLE UNITS
  // ==================================================

  unitSearch.addEventListener("input", () => {
    window.clearTimeout(searchTimer);

    const searchValue = unitSearch.value.trim();

    if (activeRequest) {
      activeRequest.abort();
      activeRequest = null;
    }

    if (searchValue.length === 0) {
      hideSearchResults();
      return;
    }

    if (searchValue.length < 2) {
      searchResults.innerHTML = `
        <div class="search-message">
          Type at least 2 characters...
        </div>
      `;
      searchResults.hidden = false;
      return;
    }

    searchTimer = window.setTimeout(() => {
      searchUnits(searchValue);
    }, 300);
  });

  async function searchUnits(searchValue) {
    activeRequest = new AbortController();

    searchResults.innerHTML = `
      <div class="search-message">
        <i class="fa-solid fa-spinner fa-spin"></i>
        Searching available units...
      </div>
    `;
    searchResults.hidden = false;

    try {
      const response = await fetch(
        `/deployment/search-units?search=${encodeURIComponent(searchValue)}`,
        {
          signal: activeRequest.signal,
          headers: {
            Accept: "application/json",
          },
        }
      );

      if (!response.ok) {
        throw new Error("Search request failed.");
      }

      const data = await response.json();
      searchResults.innerHTML = "";

      const availableResults = (data.units || []).filter(
        (unit) =>
          !selectedUnits.some(
            (selected) => Number(selected.id) === Number(unit.id)
          )
      );

      if (availableResults.length === 0) {
        searchResults.innerHTML = `
          <div class="search-message">
            <i class="fa-solid fa-circle-info"></i>
            No additional available units found.
          </div>
        `;
        searchResults.hidden = false;
        return;
      }

      availableResults.forEach((unit) => {
        const resultButton = document.createElement("button");
        resultButton.type = "button";
        resultButton.className = "unit-search-item";

        resultButton.innerHTML = `
          <div class="unit-search-icon">
            <i class="fa-solid fa-print"></i>
          </div>

          <div class="unit-search-information">
            <strong>${escapeHtml(unit.asset_code || "No Asset Code")}</strong>
            <span>
              ${escapeHtml(unit.brand || "")} ${escapeHtml(unit.model || "")}
            </span>
            <small>${escapeHtml(unit.unit_category || "Unit")}</small>
          </div>

          <span class="unit-search-status">Available</span>
        `;

        resultButton.addEventListener("click", () => {
          selectUnit(unit);
        });

        searchResults.appendChild(resultButton);
      });

      searchResults.hidden = false;
    } catch (error) {
      if (error.name === "AbortError") {
        return;
      }

      console.error("Unit search error:", error);

      searchResults.innerHTML = `
        <div class="search-message error">
          <i class="fa-solid fa-triangle-exclamation"></i>
          Unable to search units.
        </div>
      `;
      searchResults.hidden = false;
    } finally {
      activeRequest = null;
    }
  }

  // ==================================================
  // FORM VALIDATION
  // ==================================================

  deploymentForm.addEventListener("submit", (event) => {
    syncSelectedUnitsInput();

    if (selectedUnits.length === 0) {
      event.preventDefault();
      alert("Please select at least one available unit.");
      unitSearch.focus();
      return;
    }

    const submitButton = deploymentForm.querySelector('button[type="submit"]');

    if (submitButton) {
      submitButton.disabled = true;
      submitButton.innerHTML = `
        <i class="fa-solid fa-spinner fa-spin"></i>
        Saving Deployment...
      `;
    }
  });

  deploymentForm.addEventListener("reset", () => {
    // Run after the browser resets normal form controls.
    window.setTimeout(() => {
      selectedUnits.length = 0;
      renderSelectedUnits();
      unitSearch.value = "";
      hideSearchResults();
    }, 0);
  });

  // ==================================================
  // HIDE SEARCH RESULTS WHEN CLICKING OUTSIDE
  // ==================================================

  document.addEventListener("click", (event) => {
    if (
      !unitSearch.contains(event.target) &&
      !searchResults.contains(event.target)
    ) {
      searchResults.hidden = true;
    }
  });

  syncSelectedUnitsInput();
});
