import CURRENCIES from "./currencies.js";

document.addEventListener("DOMContentLoaded", function() {
  if (notify_user.checked) {
    notificationChoice.style.display = "";
  } else {
    notificationChoice.style.display = "none";
  }
  if (currency.value) {
    currencyAddon.innerHTML = CURRENCIES[currency.value]['singular name'];
  }
  if (document.getElementsByClassName("is-invalid").length) {
    let editModalButton = document.querySelector("[data-bs-target='#editModal']");
    if (editModalButton) {
      editModalButton.click();
    }
  }
});

notify_user.addEventListener("change", function() {
  if (this.checked) {
    notificationChoice.style.display = "";
  } else {
    notificationChoice.style.display = "none";
  }
});

currency.addEventListener("change", function() {
  if (currency.value) {
    currencyAddon.innerHTML = CURRENCIES[currency.value]['singular name'];
  } else {
    currencyAddon.innerHTML = "";
  }
});