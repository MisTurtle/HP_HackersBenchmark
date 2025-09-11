from hb_utils.maths import lerp


class AnimatedValue:
    def __init__(self, value):
        self.value, self.original_value = value, value
        self.start = value
        self.end = value
        self.duration = 0
        self.elapsed = 0
        self.loop = False
        self.animating = False
        self.after = None
        self.inverted = False
        self.easing = lambda t: t

    def animate(self, start, end, duration, loop=False, after=None, easing=None):
        self.start = start
        self.end = end
        self.duration = duration
        self.elapsed = 0
        self.loop = loop
        self.animating = True
        self.inverted = False
        self.after = after
        self.easing = easing or (lambda t: t)
        self.value = start

    def update(self, dt):
        if not self.animating or self.duration <= 0:
            return
        self.elapsed += dt * (-1 if self.inverted else 1)
        t = min(self.elapsed / self.duration, 1)
        t = self.easing(t)
        self.value = lerp(self.start, self.end, t)
        if self.elapsed >= self.duration or self.elapsed < 0:
            if self.loop:
                self.inverted = not self.inverted
                self.elapsed = self.duration if self.inverted else 0
            else:
                self.animating = False
                self.inverted = False
                self.value = self.end
                if self.after:
                    self.after()

    def __float__(self):
        return float(self.value) if isinstance(self.value, (int, float)) else 0.0