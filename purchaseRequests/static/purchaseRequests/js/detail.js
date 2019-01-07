

window.onload = function() {
    document.getElementById("acc-button").onclick = function() {
        noteSpan = document.getElementById("note-span");
        arrow = document.getElementById("arrow");
        if(noteSpan.style.display === "none") {
            // Show note
            noteSpan.style.display = "initial";
            arrow.classList.remove("fa-angle-down");
            arrow.classList.add("fa-angle-up");
        } else {
            // Hide note
            noteSpan.style.display = "none";
            arrow.classList.remove("fa-angle-up");
            arrow.classList.add("fa-angle-down");
        }
    };
}