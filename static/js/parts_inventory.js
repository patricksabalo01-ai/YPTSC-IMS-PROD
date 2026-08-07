

let selectedPartCode = null;


function openDeletePartModal(
  button
) {

  selectedPartCode =
    button.dataset.partCode;


  const partName =
    button.dataset.partName;


  const modal =
    document.getElementById(
      "deletePartModal"
    );


  const nameElement =
    document.getElementById(
      "deletePartName"
    );


  nameElement.textContent =
    partName;


  modal.classList.add(
    "show"
  );


  modal.setAttribute(
    "aria-hidden",
    "false"
  );

}


function closeDeletePartModal() {

  const modal =
    document.getElementById(
      "deletePartModal"
    );


  modal.classList.remove(
    "show"
  );


  modal.setAttribute(
    "aria-hidden",
    "true"
  );


  selectedPartCode = null;

}


// ==================================
// CANCEL DELETE
// ==================================

document
  .getElementById(
    "cancelDeletePart"
  )
  .addEventListener(
    "click",
    closeDeletePartModal
  );


// ==================================
// CLICK OVERLAY TO CLOSE
// ==================================

document
  .querySelector(
    "#deletePartModal .delete-modal-overlay"
  )
  .addEventListener(
    "click",
    closeDeletePartModal
  );


// ==================================
// CONFIRM DELETE
// ==================================

document
  .getElementById(
    "confirmDeletePart"
  )
  .addEventListener(
    "click",
    function () {

      if (
        !selectedPartCode
      ) {

        return;

      }


      const form =
        document.createElement(
          "form"
        );


      form.method = "POST";


      form.action =
        "/inventory/delete-part/"
        + encodeURIComponent(
          selectedPartCode
        );


      document.body.appendChild(
        form
      );


      form.submit();

    }
  );



function openViewPartModal(button) {

  // Get all data-* values
  // from the clicked eye button

  const data = button.dataset;


  // Put the selected Part data
  // into the modal fields

  document.getElementById(
    "viewPartCode"
  ).value = data.partCode;


  document.getElementById(
    "viewPartCategory"
  ).value = data.category;


  document.getElementById(
    "viewPartNumber"
  ).value = data.partNumber;


  document.getElementById(
    "viewPartDescription"
  ).value = data.description;


  document.getElementById(
    "viewPartBrand"
  ).value = data.brand;


  document.getElementById(
    "viewPartCompatibleModel"
  ).value = data.compatibleModel;


  document.getElementById(
    "viewPartSupplier"
  ).value = data.supplier;


  document.getElementById(
    "viewPartStock"
  ).value = data.stock;


  document.getElementById(
    "viewPartMinimumStock"
  ).value = data.minimumStock;


  document.getElementById(
    "viewPartLocation"
  ).value = data.location;


  document.getElementById(
    "viewPartStatus"
  ).value = data.status;


  document.getElementById(
    "viewPartRemarks"
  ).value = data.remarks;


  // Open the modal

  const modal =
    document.getElementById(
      "viewPartModal"
    );


  modal.classList.add(
    "show"
  );


  modal.setAttribute(
    "aria-hidden",
    "false"
  );


  // Prevent the page behind
  // the modal from scrolling

  document.body.style.overflow =
    "hidden";

}


function closeViewPartModal() {

  const modal =
    document.getElementById(
      "viewPartModal"
    );


  // Hide the modal

  modal.classList.remove(
    "show"
  );


  modal.setAttribute(
    "aria-hidden",
    "true"
  );


  // Restore page scrolling

  document.body.style.overflow =
    "";

}


// Close the modal using ESC

document.addEventListener(
  "keydown",
  function(event) {

    if (
      event.key === "Escape"
    ) {

      closeViewPartModal();

    }

  }
);

