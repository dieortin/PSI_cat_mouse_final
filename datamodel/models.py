from datetime import datetime
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

# class SingletonModel(models.Model):
#     class Meta:
#         abstract = True
#
#     def save(self, *args, **kwargs):
#         self.pk = 1
#         super(SingletonModel, self).save(*args, **kwargs)
#
#     def delete(self, *args, **kwargs):
#         pass
#
#     @classmethod
#     def load(cls):
#         obj, created = cls.objects.get_or_create(pk=1)
#         return obj


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
            if not valid_square(e):
                raise ValidationError("Invalid cell for a cat or the mouse")

        super().clean()

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


def valid_square(position):
    if position > Game.MAX_CELL or position < Game.MIN_CELL:
        return False
    row = (position // 8) + 1
    row_is_even = row % 2 == 0
    square_is_even = position % 2 == 0
    if row_is_even == square_is_even:
        return False

    return True


def valid_jump(origin, destination, is_mouse, game):
    if not valid_square(origin) or not valid_square(destination):
        return False

    # No puede haber ya una pieza allí, aunque sea ella misma
    if destination in [game.cat1, game.cat2, game.cat3, game.cat4, game.mouse]:
        return False
    if is_mouse:
        if abs(origin - destination) in [7, 9]:
            return True
        else:
            return False
    if not is_mouse:
        if destination - origin in [7, 9]:
            return True
        else:
            return False


def get_valid_jumps(origin, user, game):
    is_mouse = user == game.mouse_user

    # Comprobar si es su turno
    if is_mouse == game.cat_turn:
        return []

    valid_jumps = []
    if is_mouse:
        rg = [-9, -7, 7, 9]
    else:
        rg = [7, 9]
    for i in rg:
        if valid_jump(origin, origin + i, is_mouse, game):
            valid_jumps.append(origin + i)

    return valid_jumps


class Move(models.Model):
    origin = models.IntegerField(null=False, blank=False)
    target = models.IntegerField(null=False, blank=False)
    game = models.ForeignKey(Game, null=True, on_delete=models.CASCADE,
                             related_name="moves")
    player = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField(null=False, default=datetime.now)

    def save(self, *args, **kwargs):
        self.clean()

        if self.origin == self.game.cat1:
            self.game.cat1 = self.target
        elif self.origin == self.game.cat2:
            self.game.cat2 = self.target
        elif self.origin == self.game.cat3:
            self.game.cat3 = self.target
        elif self.origin == self.game.cat4:
            self.game.cat4 = self.target
        elif self.origin == self.game.mouse:
            self.game.mouse = self.target

        self.game.cat_turn = not self.game.cat_turn

        self.game.save()

        super().save(*args, **kwargs)

    def clean(self):
        if not self.game:
            if not valid_square(self.origin) or not valid_square(self.target):
                raise ValidationError("Move not allowed")

        else:
            if self.game.status != GameStatus.ACTIVE:
                raise ValidationError("Move not allowed")
            if not valid_jump(self.origin, self.target,
                              self.player == self.game.mouse_user, self.game):
                raise ValidationError("Move not allowed")
            # Solo pueden mover los jugadores
            if self.player != self.game.cat_user and self.player != self.game.mouse_user:
                raise ValidationError("Move not allowed")

            # for e in [self.game.cat1, self.game.cat2, self.game.cat3,
            #           self.game.cat4, self.game.mouse]:
            #     if e == self.target and self.target != self.origin:
            #         raise ValidationError("Move not allowed")
            # if self.origin not in [self.game.cat1, self.game.cat2,
            #                        self.game.cat3, self.game.cat4,
            #                        self.game.mouse]:
            #     raise ValidationError("Move not allowed")

            # No se puede mover fuera de turno
            if self.player == self.game.mouse_user and self.game.cat_turn:
                raise ValidationError("Move not allowed")
            elif self.player == self.game.cat_user and not self.game.cat_turn:
                raise ValidationError("Move not allowed")

            # Los gatos no pueden mover hacia atrás
            # if self.origin != self.game.mouse and self.target < self.origin:
            #     raise ValidationError("Move not allowed")

    # class SingletonModel(models.Model):


#     def validate_single_instance(self):
#         if self.objects.count() > 0 and self.id != self.objects.get().id:
#             raise ValidationError("Insert not allowed")
#
#     def clean(self):
#         self.validate_single_instance()
#         super(SingletonModel, self).clean()

class CounterManager(models.Manager):
    def create(self, *args, **kwargs):
        raise ValidationError("Insert not allowed - Create")

    def get_or_create_counter(self):
        try:
            c = super(CounterManager, self).get()
        except Counter.DoesNotExist:
            c = Counter()

        super(Counter, c).save()
        return c

    def get_current_value(self):
        c = self.get_or_create_counter()
        return c.value

    def inc(self):
        c = self.get_or_create_counter()
        c.value += 1
        super(Counter, c).save()

        return c.value


class Counter(models.Model):
    value = models.PositiveIntegerField(default=0, editable=False)
    objects = CounterManager()

    def save(self, *args, **kwargs):
        raise ValidationError("Insert not allowed")
