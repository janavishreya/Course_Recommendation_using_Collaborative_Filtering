// Show the popup with course details
function showPopup(courseId) {
    document.getElementById("course-name").textContent = `Selected Course ID: ${courseId}`;
    document.getElementById("popup").style.display = "flex";
}

// Close the popup
function closePopup() {
    document.getElementById("popup").style.display = "none";
}
