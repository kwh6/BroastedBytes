// Slideshow logic
let slideIndex = 0;
function showSlides() {
  const slides = document.getElementsByClassName("slide");
  for (let slide of slides) {
    slide.style.display = "none";
  }
  slideIndex++;
  if (slideIndex > slides.length) slideIndex = 1;
  if (slides[slideIndex - 1]) {
    slides[slideIndex - 1].style.display = "block";
  }
  setTimeout(showSlides, 3000);
}
showSlides();

// Dropdown logic with mutation observer fallback
function setupDropdown() {
  const dropBtn = document.querySelector(".dropbtn");
  const dropdownContent = document.querySelector(".dropdown-content");

  if (dropBtn && dropdownContent) {
    dropBtn.addEventListener("click", (e) => {
      e.preventDefault();
      dropdownContent.style.display =
        dropdownContent.style.display === "block" ? "none" : "block";
    });

    window.addEventListener("click", (e) => {
      if (!e.target.closest(".dropdown")) {
        dropdownContent.style.display = "none";
      }
    });
  }
}

// Wait until the page is fully loaded and ready
document.addEventListener("DOMContentLoaded", () => {
  setupDropdown();

  // Optional: observe future changes (if dropdown loads dynamically)
  const observer = new MutationObserver(setupDropdown);
  observer.observe(document.body, { childList: true, subtree: true });
});
