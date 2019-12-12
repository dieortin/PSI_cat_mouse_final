from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.db.models import Q
from django.http import HttpResponseForbidden, HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse

from datamodel import constants
from datamodel.models import Counter, Game, GameStatus, get_valid_jumps, Move
from logic.forms import UserForm, SignupForm, MoveForm


def anonymous_required(f):
    def wrapped(request):
        if request.user.is_authenticated:
            return HttpResponseForbidden(
                errorHTTP(request,
                          exception="Action restricted to anonymous users"))
        else:
            return f(request)

    return wrapped


def index(request):
    return render(request, "mouse_cat/index.html")


@login_required
def logout_service(request):
    # request.session[constants.COUNTER_SESSION_ID] = 0
    # request.session[constants.COUNTER_GLOBAL_ID] = None
    logout(request)
    return render(request, "mouse_cat/logout.html")


@anonymous_required
def login_service(request):
    if request.method == 'POST':
        user_form = UserForm(request.POST)

        if user_form.is_valid():
            username = user_form.cleaned_data.get("username")
            password = user_form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)

            if user is not None:
                if user.is_active:
                    login(request, user)
                    request.session[constants.COUNTER_SESSION_ID] = 0
                return render(request, "mouse_cat/index.html")

    else:
        user_form = UserForm()

    return render(request, "mouse_cat/login.html",
                  {'user_form': user_form})


def errorHTTP(request, exception=None):
    context_dict = {}
    context_dict[constants.ERROR_MESSAGE_ID] = exception
    return render(request, "mouse_cat/error.html", context_dict)


@anonymous_required
def signup_service(request):
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            user = form.save()
            user.set_password(user.password)
            user.save()

            u = authenticate(username=user.username, password=user.password)

            if u is not None:
                if u.is_active:
                    login(request, u)
                    request.session[constants.COUNTER_SESSION_ID] = 0
            return render(request, "mouse_cat/signup.html")

    else:
        form = SignupForm()

    return render(request, "mouse_cat/signup.html", {"user_form": form})


def counter_service(request):
    Counter.objects.inc()

    if constants.COUNTER_SESSION_ID not in request.session:
        request.session[constants.COUNTER_SESSION_ID] = 1
    else:
        request.session[constants.COUNTER_SESSION_ID] += 1

    request.session[
        constants.COUNTER_GLOBAL_ID] = Counter.objects.get_current_value()

    return render(request, "mouse_cat/counter.html", {
        "counter_session": request.session[constants.COUNTER_SESSION_ID],
        "counter_global": request.session[constants.COUNTER_GLOBAL_ID]
    })


@login_required
def create_game_service(request):
    newGame = Game.objects.create(cat_user=request.user)
    newGame.save()

    return render(request, "mouse_cat/new_game.html", {
        constants.SUCCESS_MESSAGE_ID: "Game creation complete"
    })


@login_required
def join_game_service(request):
    highestIdGame = Game.objects.filter(mouse_user=None).exclude(
        cat_user=request.user).order_by(
        "-id").first()
    if highestIdGame is not None:
        highestIdGame.mouse_user = request.user
        print("Setting highestIdGame {} mouse user to {}".format(highestIdGame,
                                                                 request.user))
        highestIdGame.save()
        return render(request, "mouse_cat/join_game.html", {
            constants.SUCCESS_MESSAGE_ID: "Joined a game with {} successfully!".format(
                highestIdGame.cat_user)
        })
    else:
        return render(request, "mouse_cat/join_game.html", {
            constants.ERROR_MESSAGE_ID: "There are no available games",
            "no_games": True
        })


@login_required
def select_game_service(request, game_id=None):
    if request.method == "GET":
        if game_id is None:
            active_games = Game.objects.filter(status=GameStatus.ACTIVE)
            games_as_cat = active_games.filter(cat_user=request.user)
            games_as_mouse = active_games.filter(mouse_user=request.user)

            if games_as_cat.count() == 0:
                games_as_cat = None
            if games_as_mouse.count() == 0:
                games_as_mouse = None

            return render(request, "mouse_cat/select_game.html", {
                "as_cat": games_as_cat,
                "as_mouse": games_as_mouse
            })
        else:
            try:
                e = Game.objects.get(id=game_id)
                if e.status != GameStatus.ACTIVE or (
                        (e.cat_user != request.user) and (
                        e.mouse_user != request.user)):
                    return HttpResponse(status=404)
                request.session[constants.GAME_SELECTED_SESSION_ID] = game_id
                return redirect(reverse('show_game'))
            except Game.DoesNotExist:
                return HttpResponse(status=404)


@login_required
def ajax_is_it_my_turn(request):
    if not constants.GAME_SELECTED_SESSION_ID in request.session:
        return HttpResponse(status=404)

    try:
        game = Game.objects.get(
            id=request.session[constants.GAME_SELECTED_SESSION_ID])
    except Game.DoesNotExist:
        return HttpResponse(status=404)

    if game.status == GameStatus.FINISHED:
        return JsonResponse({"my_turn": True})

    if (game.cat_turn and (game.cat_user == request.user)) or (
            not game.cat_turn and game.mouse_user == request.user):
        return JsonResponse({"my_turn": True})
    else:
        return JsonResponse({"my_turn": False})


@login_required
def show_game_service(request):
    if not constants.GAME_SELECTED_SESSION_ID in request.session:
        return HttpResponse(status=404)

    try:
        game = Game.objects.get(
            id=request.session[constants.GAME_SELECTED_SESSION_ID])
    except Game.DoesNotExist:
        return HttpResponse(status=404)

    board = []

    for i in range(0, 64):
        board.append({
            "number": i,
            "mouse": False,
            "cat": False
        })

    board[game.mouse]["mouse"] = True

    for e in [game.cat1, game.cat2, game.cat3, game.cat4]:
        board[e]["cat"] = True

    form = MoveForm()

    if game.cat_user == request.user:
        user_is_cat = True
    else:
        user_is_cat = False

    return render(request, "mouse_cat/game.html",
                  {"game": game, "board": board, "move_form": form,
                   "user_is_cat": user_is_cat,
                   "is_active": game.status == GameStatus.ACTIVE})


@login_required
def get_possible_moves_from_position(request, position):
    if not constants.GAME_SELECTED_SESSION_ID in request.session:
        return HttpResponse(status=404)

    try:
        game = Game.objects.get(
            id=request.session[constants.GAME_SELECTED_SESSION_ID])
    except Game.DoesNotExist:
        return HttpResponse(status=404)

    valid_jumps = get_valid_jumps(position, request.user, game)
    return JsonResponse({"valid_jumps": valid_jumps})


@login_required
def ajax_make_move(request, origin, target):
    if constants.GAME_SELECTED_SESSION_ID not in request.session:
        return HttpResponse(status=404)

    try:
        game = Game.objects.get(
            id=request.session[constants.GAME_SELECTED_SESSION_ID])
    except Game.DoesNotExist:
        return HttpResponse(status=404)

    try:
        newMove = Move(origin=origin, target=target, player=request.user,
                       game=game)
        newMove.save()
        return HttpResponse(status=200)
    except ValidationError:
        return HttpResponse("El movimiento no está permitido", status=403)
        # Movimiento no válido



@login_required
def move_service(request):
    if request.method == "GET" or constants.GAME_SELECTED_SESSION_ID not in request.session:
        return HttpResponse(status=404)
    elif request.method == "POST":
        moveF = MoveForm(request.POST)
        if moveF.is_valid():
            print("bbellowefqwef")
            newMove = moveF.save(commit=False)
            try:
                game = Game.objects.get(
                    id=request.session[constants.GAME_SELECTED_SESSION_ID])
            except Game.DoesNotExist:
                return HttpResponse(status=404)
            newMove.game = game
            newMove.player = request.user
            newMove.save()
            return HttpResponse(status=200)
        return HttpResponse(status=304)
