function toggleLanguage() {
    const currentPath = window.location.pathname;
    const parts = currentPath.split('/');
    const currentLang = parts[1];

    let newLang = currentLang === 'en' ? 'es' : 'en';
    parts[1] = newLang;

    const newPath = parts.join('/');
    window.location.href = newPath;
}
