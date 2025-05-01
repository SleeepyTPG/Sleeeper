// Select the Dark Mode toggle button and icon
const darkModeToggle = document.getElementById("dark-mode-toggle");
const darkModeIcon = document.getElementById("dark-mode-icon");

// Add an event listener to toggle Dark Mode
darkModeToggle.addEventListener("click", () => {
    // Toggle the "dark-mode" class on the body
    document.body.classList.toggle("dark-mode");

    // Toggle the "dark-mode" class on other elements
    document.querySelector("header").classList.toggle("dark-mode");
    document.querySelectorAll(".feature").forEach(feature => feature.classList.toggle("dark-mode"));
    document.querySelectorAll(".command").forEach(command => command.classList.toggle("dark-mode"));
    document.querySelector("footer").classList.toggle("dark-mode");

    // Switch the icon between sun and moon
    if (document.body.classList.contains("dark-mode")) {
        darkModeIcon.textContent = "🌙"; // Moon icon for dark mode
    } else {
        darkModeIcon.textContent = "☀️"; // Sun icon for light mode
    }
});

function toggleDetails(id) {
    const details = document.getElementById(id);

    // Toggle the "show" class for the clicked details section
    details.classList.toggle("show");
}