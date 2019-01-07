

window.onload = function() {
    document.getElementById("acc-button").onclick = function() {
        noteSpan = document.getElementById("note-span");
        if(noteSpan.style.display === "none") {
            noteSpan.style.display = "initial";
        } else {
            noteSpan.style.display = "none";
        }
    };
}