let closeButtons;

document.addEventListener("DOMContentLoaded", function() {
  closeButtons = document.getElementsByClassName("btn-close");

  for (let closeButton of closeButtons) {
    if (closeButton.hasAttribute("data-item-id")) {
      closeButton.addEventListener("click", function() {
        deleteForm.action = "/items/" + this.getAttribute("data-item-id") + "/delete";
        deleteModalLabel.innerHTML = "Delete " + this.getAttribute("data-item-name") + "?";
      });
    }
  }
});