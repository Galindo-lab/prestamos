// IMPORTANTE: coloca esto en el <HEAD> antes de cualquier otra etiqueta.
const setTheme = (theme) => {
    theme = theme || localStorage.getItem('appTheme') || "light"; // Asegura la asignación correcta
    document.documentElement.setAttribute('data-bs-theme', theme);
    localStorage.setItem('appTheme', theme); // Guarda el tema en localStorage correctamente
    console.log(theme); // Verifica el tema que se está asignando
};

setTheme(); // Inicializa el tema al cargar la página

window.onpageshow = function (event) {
    if (event.persisted) { // Para manejar la recarga desde el caché
        setTheme();
    }
};
