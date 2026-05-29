const navToggle = document.querySelector(".nav-toggle");
const navLinks = document.querySelector("#nav-links");

if (navToggle && navLinks) {
  navToggle.addEventListener("click", () => {
    const isOpen = navLinks.classList.toggle("is-open");
    navToggle.setAttribute("aria-expanded", String(isOpen));
  });

  navLinks.addEventListener("click", (event) => {
    if (event.target instanceof HTMLAnchorElement) {
      navLinks.classList.remove("is-open");
      navToggle.setAttribute("aria-expanded", "false");
    }
  });
}

const observedSections = document.querySelectorAll("main section[id]");
const navAnchors = document.querySelectorAll('.nav-links a[href^="#"]');

if ("IntersectionObserver" in window && observedSections.length > 0) {
  const observer = new IntersectionObserver(
    (entries) => {
      const visible = entries
        .filter((entry) => entry.isIntersecting)
        .sort((a, b) => b.intersectionRatio - a.intersectionRatio)[0];

      if (!visible) {
        return;
      }

      navAnchors.forEach((anchor) => {
        anchor.toggleAttribute(
          "aria-current",
          anchor.getAttribute("href") === `#${visible.target.id}`,
        );
      });
    },
    {
      rootMargin: "-30% 0px -55% 0px",
      threshold: [0.1, 0.3, 0.6],
    },
  );

  observedSections.forEach((section) => observer.observe(section));
}
