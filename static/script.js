document.addEventListener('DOMContentLoaded', () => {
    // --- Mobile Navigation Toggle ---
    const nav = document.querySelector(".primary-navigation");
    const navToggle = document.querySelector(".mobile-nav-toggle");

    navToggle.addEventListener("click", () => {
        const visibility = nav.getAttribute("data-visible");
        if (visibility === "false") {
            nav.setAttribute("data-visible", true);
            navToggle.setAttribute("aria-expanded", true);
        } else {
            nav.setAttribute("data-visible", false);
            navToggle.setAttribute("aria-expanded", false);
        }
    });

    // --- Scroll-Spy for Active Navigation Link ---
    const sections = document.querySelectorAll('section[id]');
    const navLinks = document.querySelectorAll('.primary-navigation .nav-link');
    const headerOffset = document.querySelector('.primary-header').offsetHeight;

    const onScroll = () => {
        const scrollPosition = window.scrollY + headerOffset + 1;

        let activeSectionId = null;

        sections.forEach(section => {
            if (scrollPosition >= section.offsetTop && scrollPosition < section.offsetTop + section.offsetHeight) {
                activeSectionId = section.id;
            }
        });

        navLinks.forEach(link => {
            link.classList.remove('active');
            // The href is a full URL, so we check if it ends with the section ID
            if (activeSectionId && link.href.endsWith('#' + activeSectionId)) {
                link.classList.add('active');
            }
        });
    };

    // Add event listener for scroll
    window.addEventListener('scroll', onScroll);

    // Run on page load to set the initial state
    onScroll();
});