from enum import auto, IntEnum

from django.db import models
from django.contrib.auth.models import User


class GameStatus(IntEnum):
    CREATED = auto()
    ACTIVE = auto()
    FINISHED = auto()

    @classmethod
    def choices(cls):
        return [(i.value, i.name) for i in cls]


# class GameStatus:
#     CREATED = "C"
#     ACTIVE = "A"
#     FINISHED = "F"
#
#     choices = [
#         (CREATED, "Created"),
#         (ACTIVE, "Active"),
#         (FINISHED, "Finished"),
#     ]


# Create your models here.
# class UserData(models.Model):
#    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Game(models.Model):
    MIN_CELL = 0
    MAX_CELL = 63

    cat_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="catuser_game")
    mouse_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="mouseuser_game")

    # Cat positions
    cat1 = models.IntegerField(null=False, blank=False, default=0, editable=False)
    cat2 = models.IntegerField(null=False, blank=False, default=2, editable=False)
    cat3 = models.IntegerField(null=False, blank=False, default=4, editable=False)
    cat4 = models.IntegerField(null=False, blank=False, default=6, editable=False)

    # Mouse position
    mouse = models.IntegerField(null=False, blank=False, default=59, editable=False)

    # Turn indicator: true if it's the cat's turn, false otherwise
    cat_turn = models.BooleanField(null=False, blank=False, default=True)

    # Current game status
    status = models.IntegerField(choices=GameStatus.choices(), null=False, max_length=64,
                              default=GameStatus.CREATED)

    def save(self, *args, **kwargs):
        if self.mouse_user and self.status == GameStatus.CREATED:
            self.status = GameStatus.ACTIVE
        super().save(*args, **kwargs)


    def __str__(self):
        string = "({}, {})\t".format(self.id, self.status)
        if self.cat_turn:
            string += "Cat [X] "
        else:
            string += "Cat [ ] "
        string += "{}({}, {}, {}, {})".format(self.cat_user.get_username(), self.cat1, self.cat2, self.cat3, self.cat4)

        if self.mouse_user:
            if self.cat_turn:
                string += "--- Mouse[ ] "
            else:
                string += "--- Mouse[X] "
            string += "{}({})".format(self.mouse_user.get_username(), self.mouse)
        return string


class Move(models.Model):
    origin = models.IntegerField(null=False, blank=False)
    target = models.IntegerField(null=False, blank=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(null=False)
