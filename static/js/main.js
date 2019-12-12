$(document).ready(function () {
    (function worker() {
        $.ajax({
            url: '/ajax_is_it_my_turn',
            success: function (data) {
                if (data["my_turn"] === false) {
                    setTimeout(worker, 5000);
                }
            }
        });
    })();
    $(".square").click(function () {
        if ($(this).hasClass("possible-move")) {
            let pos = $(this).attr('id').replace("square-", "");
            makeMove(selectedOrigin, pos);
        } else {
            removeSelectedAndPossible();
            selectedOrigin = null;
        }
    });
    $(".ours").parent().parent().click(function () {
        removeSelectedAndPossible();
        $(this).addClass("selected-piece");
        let pos = $(this).attr('id').replace("square-", "");
        selectedOrigin = pos;
        requestPossibleMoves(pos)
    })
});

function removeSelectedAndPossible() {
    $(".selected-piece, .possible-move").removeClass("selected-piece possible-move");
}

let selectedOrigin = null;

function requestPossibleMoves(position) {
    $.ajax({
        url: '/get_possible_moves_from_position/' + position,
        success: function (result) {
            validJumpIds = [];
            result["valid_jumps"].forEach(element => validJumpIds.push("square-" + element));
            validJumpIds.forEach(elementId => {
                console.log(elementId);
                console.log($("#" + elementId));
                $('#' + elementId).addClass("possible-move")
            })
        }
    })
}

function makeMove(origin, target) {
    $.ajax({
        url: "/ajax_make_move/" + origin + "/" + target,
        success: function (result) {
            $("#square-" + origin + " img").appendTo($("#square-" + target));
            console.log($(".selected-piece, .possible-move"));
            $(".selected-piece, .possible-move").removeClass("selected-piece possible-move");
            $("#cat-waiting, #mouse-waiting").removeClass("hidden");
            (function worker() {
                $.ajax({
                    url: '/ajax_is_it_my_turn',
                    success: function (data) {
                        if (data["my_turn"]) {
                            location.reload();
                        }
                    },
                    complete: function () {
                        // Schedule the next request when the current one's complete
                        setTimeout(worker, 5000);
                    }
                });
            })();
        },
        error: function (xhr, ajaxOptions, thrownError) {
            alert(thrownError)
        }
    })
}

