

$(function() {
    $(".accordion").click(function() {
        noteSpan = $("#note-span");
        arrow = $("#arrow");
        if(noteSpan.css("display") === "none") {
            // Show note
            noteSpan.css("display", "initial");
            arrow.removeClass("fa-angle-down");
            arrow.addClass("fa-angle-up");
        } else {
            // Hide note
            noteSpan.css("display", "none");
            arrow.removeClass("fa-angle-up");
            arrow.addClass("fa-angle-down");
        }
    });
});