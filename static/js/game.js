$(document).ready(function () {
    // If it isn't my turn, keep checking periodically for it and reload when that changes
    isItMyTurn(function (myTurn) {
        if (!myTurn) {
            console.log("not my turn");
            $('#cat-waiting, #mouse-waiting').removeClass('hidden');
            (function worker() {
                isItMyTurn(function (d) {
                    if (!d) {
                        setTimeout(worker, 5000);
                    } else {
                        location.reload();
                    }
                })
            })();
        }
    });
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

function isItMyTurn(handler) {
    $.ajax({
        url: '/ajax_is_it_my_turn',
        success: function (data) {
            handler(data["my_turn"]);
        }
    });
}

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
        success: function () {
            $("#square-" + origin + " img").appendTo($("#square-" + target));
            $(".selected-piece, .possible-move").removeClass("selected-piece possible-move");
            $("#cat-waiting, #mouse-waiting").removeClass("hidden");
            (function worker() {
                isItMyTurn(function (d) {
                    if (!d) {
                        setTimeout(worker, 2000);
                    } else {
                        location.reload();
                    }
                })
            })();
        },
        error: function (xhr, ajaxOptions, thrownError) {
            alert(thrownError)
        }
    })
}
