
const joinForm = document.getElementById("join-form");
if (joinForm) {
  joinForm.addEventListener("submit", () => {
    const button = joinForm.querySelector("button[type=submit]");
    button.disabled = true;
    button.textContent = "Getting your ticket…";
  });
}

// Plate field: capital letters, numbers, spaces and hyphens only
const plateInput = document.getElementById("plate");
if (plateInput) {
  plateInput.setAttribute("autocapitalize", "characters");
  plateInput.setAttribute("maxlength", "12");
  plateInput.addEventListener("input", () => {
    plateInput.value = plateInput.value.toUpperCase().replace(/[^A-Z0-9 -]/g, "");
  });
}

// Staff: select all / select specific trucks
const selectAll = document.getElementById("select-all");
const callSelected = document.getElementById("call-selected");
const rowBoxes = () => Array.from(document.querySelectorAll("input[name=ticket_ids]"));

function updateSelected() {
  const boxes = rowBoxes();
  const n = boxes.filter(b => b.checked).length;
  if (callSelected) {
    callSelected.textContent = `Call selected (${n})`;
    callSelected.disabled = n === 0;
  }
  if (selectAll) {
    selectAll.checked = boxes.length > 0 && n === boxes.length;
    selectAll.indeterminate = n > 0 && n < boxes.length;
  }
}

if (selectAll) {
  selectAll.addEventListener("change", () => {
    rowBoxes().forEach(b => { b.checked = selectAll.checked; });
    updateSelected();
  });
}
rowBoxes().forEach(b => b.addEventListener("change", updateSelected));
updateSelected();