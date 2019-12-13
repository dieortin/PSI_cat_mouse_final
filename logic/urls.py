from django.urls import path

from logic import views

urlpatterns = [
    path('index/', views.index, name="index"),
    path('', views.index, name="landing"),
    path('login_service/', views.login_service, name="login"),
    path('logout_service/', views.logout_service, name='logout'),
    path('signup_service/', views.signup_service, name='signup'),
    path('counter_service/', views.counter_service, name='counter'),
    path('create_game_service/', views.create_game_service,
         name='create_game'),
    # path('join_game_service/', views.join_game_service, name='join_game'),
    path('select_game_service/<int:game_id>/', views.select_game_service,
         name='select_game'),
    path('select_game_service/', views.select_game_service,
         name='select_game'),
    path('show_game_service/', views.show_game_service, name='show_game'),
    path('move_service/', views.move_service, name='move'),
    path('ajax_make_move/<int:origin>/<int:target>', views.ajax_make_move,
         name="ajax_make_move"),
    path('get_possible_moves_from_position/<int:position>',
         views.get_possible_moves_from_position, name='get_possible_moves'),
    path('ajax_is_it_my_turn', views.ajax_is_it_my_turn,
         name='ajax_is_it_my_turn'),
    path('how_to_play', views.how_to_play, name='manual'),
    path('replay_move/<int:move>/<int:reverse>', views.replay_move,
         name='replay_move'),
    path('next_move/<int:backwards>', views.next_move, name='next_move')
]
