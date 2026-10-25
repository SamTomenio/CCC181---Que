// Served at /static/js/main.js and linked from templates/base.html.
console.log("ClinicQ starter app loaded");

const plateInput = document.getElementById("plate");
if (plateInput) {
  plateInput.setAttribute("autocapitalize", "characters");
  plateInput.setAttribute("maxlength", "12");
  plateInput.addEventListener("input", () => {
    plateInput.value = plateInput.value.toUpperCase().replace(/[^A-Z0-9 -]/g, "");
  });
}