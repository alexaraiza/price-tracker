const lang = navigator.language;
let priceElements;

document.addEventListener("DOMContentLoaded", function() {
  priceElements = document.getElementsByClassName("price");

  for (let priceElement of priceElements) {
    let currency = priceElement.innerHTML.slice(0, 3);
    let price = priceElement.innerHTML.slice(3);
    if (!isNaN(price)) {
      priceElement.innerHTML = new Intl.NumberFormat(lang, {style: 'currency', currency: currency}).format(price);
    }
  }
});