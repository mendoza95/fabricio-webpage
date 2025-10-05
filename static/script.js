const primaryNav = document.querySelector('.primary-navigation');
const navToggle = document.querySelector('.mobile-nav-toggle');
const navLinks = document.querySelectorAll('.nav-link');

function setNavVisibility(visible) {
    const isVisible = visible ? 'true' : 'false';
    primaryNav.setAttribute('data-visible', isVisible);
    navToggle.setAttribute('aria-expanded', isVisible);
}

navToggle.addEventListener('click', () => {
    const visibility = primaryNav.getAttribute('data-visible');
    setNavVisibility(visibility === "false");
});

// Close the mobile menu when a link is clicked
navLinks.forEach(link => {
    link.addEventListener('click', () => {
        // Only close if the mobile nav is visible
        if (primaryNav.getAttribute('data-visible') === 'true') {
            setNavVisibility(false);
        }
    });
});

// --- Success Modal Logic ---
document.addEventListener('DOMContentLoaded', () => {
    const modal = document.getElementById('success-modal');
    const closeBtn = document.getElementById('modal-close-btn');

    if (modal && closeBtn) {
        const closeModal = () => {
            modal.classList.add('hidden');
        };

        closeBtn.addEventListener('click', closeModal);
    }
});