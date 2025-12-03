// Apply saved theme when page loads
document.addEventListener("DOMContentLoaded", function () {
    let savedTheme = localStorage.getItem("theme") || "light";
    document.body.classList.add(savedTheme);
});
