
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