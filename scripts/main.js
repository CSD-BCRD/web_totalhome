document.addEventListener("DOMContentLoaded", () => {
  // Set current year in footer
  document.getElementById("year").textContent = new Date().getFullYear();


  // Mobile Menu Toggle
  const mobileMenuBtn = document.getElementById("mobile-menu-btn");
  const mobileMenu = document.getElementById("mobile-menu");
  const mobileIcon = mobileMenuBtn.querySelector("i");
  const mobileLinks = document.querySelectorAll(".mobile-link");

  const toggleMenu = () => {
    const isHidden = mobileMenu.classList.contains("hidden");
    if (isHidden) {
      mobileMenu.classList.remove("hidden");
      // Small timeout to allow display:block to apply before animating height
      setTimeout(() => {
        mobileMenu.style.maxHeight = mobileMenu.scrollHeight + "px";
      }, 10);
      mobileIcon.classList.remove("fa-bars");
      mobileIcon.classList.add("fa-xmark");
    } else {
      mobileMenu.style.maxHeight = "0px";
      setTimeout(() => {
        mobileMenu.classList.add("hidden");
      }, 300); // match duration
      mobileIcon.classList.remove("fa-xmark");
      mobileIcon.classList.add("fa-bars");
    }
  };

  mobileMenuBtn.addEventListener("click", toggleMenu);

  // Close mobile menu when a link is clicked
  mobileLinks.forEach((link) => {
    link.addEventListener("click", () => {
      if (!mobileMenu.classList.contains("hidden")) {
        toggleMenu();
      }
    });
  });

  // Header Background transparency on scroll
  const headerBg = document.getElementById("header-bg");
  window.addEventListener("scroll", () => {
    if (window.scrollY > 10) {
      headerBg.style.opacity = "1";
      headerBg.classList.add("shadow-lg");
    } else {
      headerBg.style.opacity = "0.98"; // slightly transparent at top
      headerBg.classList.remove("shadow-lg");
    }
  });

  // Carousel Logic
  const track = document.getElementById("carousel-track");
  const prevBtn = document.getElementById("carousel-prev");
  const nextBtn = document.getElementById("carousel-next");
  if (track && prevBtn && nextBtn) {
    const slides = Array.from(track.children);
    let currentSlide = 0;
    
    const updateSlide = () => {
      track.style.transform = `translateX(-${currentSlide * 100}%)`;
    };
    
    nextBtn.addEventListener("click", () => {
      currentSlide = (currentSlide + 1) % slides.length;
      updateSlide();
    });
    
    prevBtn.addEventListener("click", () => {
      currentSlide = (currentSlide - 1 + slides.length) % slides.length;
      updateSlide();
    });
    
    // Optional auto-play
    setInterval(() => {
      currentSlide = (currentSlide + 1) % slides.length;
      updateSlide();
    }, 6000);
  }
});
