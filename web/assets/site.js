// Writing page: filter the cards and year lists by publication. Without JavaScript the filter stays hidden and every
// article is listed.
document.addEventListener("DOMContentLoaded", () => {
  const filters = document.querySelector(".rap-filters");
  if (!filters) return;
  const buttons = [...filters.querySelectorAll("button[data-filter]")];
  const articles = [...document.querySelectorAll(".rap-page [data-publication]")];
  const years = [...document.querySelectorAll(".rap-year")];
  const empty = document.querySelector(".rap-empty");
  const cards = document.querySelector(".rap-writing-cards");

  const choose = (key) => {
    buttons.forEach((button) => button.setAttribute("aria-pressed", String(button.dataset.filter === key)));
    articles.forEach((article) => { article.hidden = key !== "all" && article.dataset.publication !== key; });
    years.forEach((year) => { year.hidden = !year.querySelector("[data-publication]:not([hidden])"); });
    const anyCard = cards && cards.querySelector("[data-publication]:not([hidden])");
    if (empty) empty.hidden = Boolean(anyCard);
  };

  buttons.forEach((button) => button.addEventListener("click", () => choose(button.dataset.filter)));
  filters.hidden = false;
});
