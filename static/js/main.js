function toggleLanguage() {
    const currentPath = window.location.pathname;
    const parts = currentPath.split('/');
    const currentLang = parts[1];

    let newLang = currentLang === 'en' ? 'es' : 'en';
    parts[1] = newLang;

    const newPath = parts.join('/');
    window.location.href = newPath;
}

// Función para abrir el modal y cargar el texto actual
function openEditModal(element) {
    const collection = element.dataset.collection;
    const docId = element.dataset.id || '';
    const field = element.dataset.field;
    const lang = element.dataset.lang;
    
    // Obtener el texto limpio del elemento
    const currentText = element.innerText.trim();

    // Rellenar campos del modal
    document.getElementById('modal-collection').value = collection;
    document.getElementById('modal-id').value = docId;
    document.getElementById('modal-field').value = field;
    document.getElementById('modal-lang').value = lang;
    document.getElementById('modal-input-text').value = currentText;

    // Cambiar título del modal según el campo
    document.getElementById('modal-title').innerText = `Editar ${field}`;

    // Mostrar modal
    document.getElementById('edit-modal').style.display = 'flex';
}

function closeModal() {
    document.getElementById('edit-modal').style.display = 'none';
}

// Escuchar el evento submit del formulario dentro del modal
document.addEventListener('DOMContentLoaded', function() {
    const modalForm = document.getElementById('modal-form');
    if (modalForm) {
        modalForm.addEventListener('submit', function(e) {
            e.preventDefault();

            const saveBtn = document.getElementById('btn-save-modal');
            saveBtn.disabled = true;
            saveBtn.innerText = 'Guardando...';

            const payload = {
                collection: document.getElementById('modal-collection').value,
                id: document.getElementById('modal-id').value,
                field: document.getElementById('modal-field').value,
                lang: document.getElementById('modal-lang').value,
                text: document.getElementById('modal-input-text').value
            };

            // Enviar la actualización al backend en app.py
            fetch('/api/update-portfolio', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify(payload)
            })
            .then(response => response.json())
            .then(data => {
                if (data.status === 'success') {
                    // Recargar la página para ver los cambios reflejados
                    window.location.reload();
                } else {
                    alert('Error al guardar: ' + data.message);
                    saveBtn.disabled = false;
                    saveBtn.innerText = 'Guardar Cambios';
                }
            })
            .catch(error => {
                console.error('Error:', error);
                alert('Ocurrió un error en la comunicación con el servidor.');
                saveBtn.disabled = false;
                saveBtn.innerText = 'Guardar Cambios';
            });
        });
    }
});

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