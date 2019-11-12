from enum import auto, Enum

from django.core.exceptions import ValidationError
from django.db import models
from django.contrib.auth.models import User


# class GameStatus(Enum):
#     CREATED = "Created"
#     ACTIVE = "Active"
#     FINISHED = "Finished"
#
#     @classmethod
#     def choices(cls):
#         print(tuple((x.name, x.value) for x in cls))
#         return tuple((x.name, x.value) for x in cls)

class GameStatus():
    CREATED = "Created"
    ACTIVE = "Active"
    FINISHED = "Finished"

    choices = [
        (CREATED, "Created"),
        (ACTIVE, "Active"),
        (FINISHED, "Finished"),
    ]


# Create your models here.
# class UserData(models.Model):
#    user = models.OneToOneField(User, on_delete=models.CASCADE)


class Game(models.Model):
    MIN_CELL = 0
    MAX_CELL = 63

    cat_user = models.ForeignKey(User, on_delete=models.CASCADE,
                                 related_name="games_as_cat")
    mouse_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True,
                                   blank=True, related_name="games_as_mouse")

    # Cat positions
    cat1 = models.IntegerField(null=False, blank=False, default=0,
                               editable=False)
    cat2 = models.IntegerField(null=False, blank=False, default=2,
                               editable=False)
    cat3 = models.IntegerField(null=False, blank=False, default=4,
                               editable=False)
    cat4 = models.IntegerField(null=False, blank=False, default=6,
                               editable=False)

    # Mouse position
    mouse = models.IntegerField(null=False, blank=False, default=59,
                                editable=False)

    # Turn indicator: true if it's the cat's turn, false otherwise
    cat_turn = models.BooleanField(null=False, blank=False, default=True)

    # Current game statu
    status = models.CharField(null=False, choices=GameStatus.choices,
                              default=GameStatus.CREATED, max_length=30)

    def save(self, *args, **kwargs):
        self.clean()

        super().save(*args, **kwargs)

    def clean(self):
        if self.mouse_user and self.status == GameStatus.CREATED:
            self.status = GameStatus.ACTIVE

        for e in [self.cat1, self.cat2, self.cat3, self.cat4, self.mouse]:
            if not self.valid_square(e):
                raise ValidationError("Invalid cell for a cat or the mouse")

        super().clean()

    def valid_square(self, position):
        if position > self.MAX_CELL or position < self.MIN_CELL:
            return False
        row = (position // 8) + 1
        row_is_even = row % 2 == 0
        square_is_even = position % 2 == 0
        if row_is_even == square_is_even:
            return False

        return True

    def __str__(self):
        string = "({}, {})\t".format(self.id, self.status)
        if self.cat_turn:
            string += "Cat [X] "
        else:
            string += "Cat [ ] "
        string += "{}({}, {}, {}, {})".format(self.cat_user.get_username(),
                                              self.cat1, self.cat2, self.cat3,
                                              self.cat4)

        if self.mouse_user:
            if self.cat_turn:
                string += " --- Mouse [ ] "
            else:
                string += " --- Mouse [X] "
            string += "{}({})".format(self.mouse_user.get_username(),
                                      self.mouse)
        return string


class Move(models.Model):
    origin = models.IntegerField(null=False, blank=False)
    target = models.IntegerField(null=False, blank=False)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(null=False)
