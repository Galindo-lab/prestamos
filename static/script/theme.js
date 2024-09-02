
// IMPORTANT: set this in <HEAD> top before any other tag.
const setTheme = (theme) => {
    theme ??= localStorage.theme || "light";
    document.documentElement.setAttribute('data-bs-theme', theme);
    localStorage.theme = theme;
};

setTheme();

window.onpageshow = function (event) {
    if (event.persisted) {
        setTheme();
    }
};