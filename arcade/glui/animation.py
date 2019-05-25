import weakref

from arcade.glui.bezier import Bezier
from arcade.glui.state import State


class AnimationSystem(object):
    animation_list = []

    @classmethod
    def is_active(cls):
        return len(cls.animation_list) > 0

    @classmethod
    def update(cls, t=None):
        t = t or State.get().time
        deleted = []
        for ref_obj in cls.animation_list:
            obj = ref_obj()
            if obj is None:
                deleted.append(ref_obj)
            else:
                if not obj.update(t):
                    deleted.append(ref_obj)
        for d in deleted:
            cls.animation_list.remove(d)


class AnimateValueLinear(object):
    def __init__(
        self, what, from_value, from_time, to_value, to_time, run=True
    ):
        self.what = what
        self.from_value = from_value
        self.to_value = to_value
        self.from_time = from_time
        self.to_time = to_time
        if run:
            AnimationSystem.animation_list.append(weakref.ref(self))

    @property
    def max_time(self):
        return self.to_time

    def update(self, t=None):
        t = t or State.get().time
        progress = (t - self.from_time) / (self.to_time - self.from_time)
        progress = max(0.0, min(1.0, progress))
        setattr(
            self.what[0],
            self.what[1],
            self.from_value + progress * (self.to_value - self.from_value),
        )
        return t < self.to_time


class AnimateValueBezier(object):
    def __init__(
        self, what, x0, t0, x1, t1, x2, t2, x3, t3, points=50, run=True
    ):
        self.what = what
        self.params = (x0, t0, x1, t1, x2, t2, x3, t3)
        self.curve = Bezier.bezier(
            (t0, x0), (t1, x1), (t2, x2), (t3, x3), steps=points
        )
        if run:
            AnimationSystem.animation_list.append(weakref.ref(self))

    @property
    def max_time(self):
        return self.curve[-1][0]

    def update(self, t=None):
        x0, t0, x1, t1, x2, t2, x3, t3 = self.params
        t = t or State.get().time
        if t < t0:
            t = t0
        elif t > t3:
            t = t3
        x = Bezier.interpolate(self.curve, t)
        setattr(self.what[0], self.what[1], x)
        return t < t3


class AnimationSequence(object):
    def __init__(self, anim_seq):
        self.anim_seq = anim_seq
        AnimationSystem.animation_list.append(weakref.ref(self))

    def update(self, t=None):
        t = t or State.get().time
        for anim in self.anim_seq:
            if t > anim.max_time:
                continue
            anim.update(t)
            break
        else:
            return self.anim_seq[-1].update()
        return True
