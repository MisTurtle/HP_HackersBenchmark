import random
import pygame
import time

from hb_types.widgets import DrawingGrid, ImageWidget, TextWidget, Widget
from hb_utils.factories import ColorProvider, FontProvider
from hb_utils.maths import auto_width, ease_in_out


# TODO : Harmonize instance variable names
# TODO : Base class for game widgets (with on_complete)

class LatencyTimeWidget(Widget):

    MIN_WAIT = 1.5
    MAX_WAIT = 8.0

    def __init__(
        self,
        border_color=(255, 255, 255),
        border_radius=16,
        start_text="Clique pour commencer.",
        wait_text="Attend le vert...",
        click_text="Clique !",
        result_text="Latence: {ms} ms\nAppuie pour continuer",
        too_soon_text="Trop rapide !\nAppuie pour recommencer",
        red_color=(200, 50, 50),
        green_color=(50, 200, 50),
        on_complete=None,
        **kwargs
    ):
        super().__init__(**kwargs)

        # Appearance
        self.border_color = border_color
        self.border_radius = border_radius
        self.start_text = start_text
        self.wait_text = wait_text
        self.click_text = click_text
        self.result_text = result_text
        self.too_soon_text = too_soon_text
        self.red_color = red_color
        self.green_color = green_color
        self.on_complete = on_complete
        self.hovered = False

        # Internal state
        self.state = "ready"   # ready, waiting, green
        self._wait_until = None
        self._reaction_start = None
        self.reaction_times: list[float] = []

        self.text_widget = TextWidget(
            self.start_text, font=FontProvider.get(("Camcode.ttf", 64)), color=ColorProvider.get('bg_dark'), align='center', line_height_multiplier=1.2,
            rel_x=0.5, rel_y=0.5, rel_width=0.8, rel_height=0.1, container_rect=self.rect
        )

    def updateText(self, text: str):
        self.text_widget.text = text

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 or event.type == pygame.KEYDOWN and event.unicode != "":
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self._handle_click()

    def _handle_click(self):
        if self.state == "ready":
            # Switch to red and schedule green after random delay
            self.state = "waiting"
            self._wait_until = time.time() + LatencyTimeWidget.MIN_WAIT + (LatencyTimeWidget.MAX_WAIT - LatencyTimeWidget.MIN_WAIT) * random.random()
            self.updateText(self.wait_text)

        elif self.state == "waiting":
            # Clicked too early
            self.state = "ready"
            self._wait_until = None
            self.updateText(self.too_soon_text)

        elif self.state == "green":
            # Valid reaction
            reaction_time = (time.time() - self._reaction_start) * 1000.0
            self.reaction_times.append(reaction_time)
            self.updateText(self.result_text.format(ms=int(reaction_time)))
            self.state = "ready"

            if len(self.reaction_times) >= 3:
                if self.on_complete:
                    self.on_complete()

    def update(self, dt: float):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)
        if is_hovered != self.hovered:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if is_hovered else pygame.SYSTEM_CURSOR_ARROW)

        if self.state == "waiting" and self._wait_until is not None:
            if time.time() >= self._wait_until:
                self.state = "green"
                self._reaction_start = time.time()
                self.updateText(self.click_text)
                

    def draw(self, surface: pygame.Surface):
        # Pick background color based on state
        if self.state in ("green", "ready"):
            color = self.green_color
        elif self.state == "waiting":
            color = self.red_color
        else:
            return

        pygame.draw.rect( surface, color, self.rect, border_radius=self.border_radius )
        pygame.draw.rect( surface, self.border_color, self.rect, width=3, border_radius=self.border_radius )
        self.text_widget.draw(surface)


class BugHunterGameWidget(Widget):

    def __init__(self, bug_image, bug_mov_dur = 0.08, n_targets: int = 12, on_complete=None, **kwargs):
        super().__init__(**kwargs)
        self._bug_image = ImageWidget(bug_image, self.click, rel_x=0.5, rel_y=0.5, rel_height=0.2, rel_width=auto_width(0.2, bug_image.get_size(), self.rect.size), container_rect=self.rect)
        self._counter = TextWidget(text=str(n_targets), font=FontProvider.get(('Camcode.ttf', 72)), color=ColorProvider.get('bg_dark_lighter'), align='center', rel_x=0.5, rel_y=-0.1, rel_width=0.1, rel_height=0.1, container_rect=self.rect)
        self._bug_mov_dur = bug_mov_dur
        self._n_targets = n_targets
        self._scores = []
        self._last_click = time.time()
        self._moving = False
        self._first = True
        self.on_complete = on_complete

    def click(self):
        if self._moving:
            return
        self._moving = True
        if not self._first:
            self._scores.append((time.time() - self._last_click) * 1000)
            if len(self._scores) >= self._n_targets and self.on_complete:
                self.on_complete()
                return
            
            self._counter.text = str(self._n_targets - len(self._scores))
            
        self._first = False
        
        new_x = random.random()
        while abs(new_x - self._bug_image.rel_x.value) < 0.25:
            new_x = random.random()

        new_y = random.random()
        while abs(new_y - self._bug_image.rel_y.value) < 0.25:
            new_y = random.random()

        self._bug_image.rel_x.animate(self._bug_image.rel_x.value, new_x, self._bug_mov_dur, easing=ease_in_out)
        self._bug_image.rel_y.animate(self._bug_image.rel_y.value, new_y, self._bug_mov_dur, after=self.enable_click, easing=ease_in_out)

        self._last_click = time.time()
    
    def enable_click(self):
        self._moving = False

    def handle_event(self, event):
        super().handle_event(event)  # TODO Running out of time right now, but make a container module instead of listing dependent widgets like that
        self._bug_image.handle_event(event)
        self._counter.handle_event(event)

    def update(self, dt):
        super().update(dt)
        self._bug_image.update(dt)
        self._counter.update(dt)

    def draw(self, surface):
        self._counter.draw(surface)
        self._bug_image.draw(surface)


class TimeMasterWidget(Widget):

    def __init__(
        self,
        border_color=(255, 255, 255),
        border_radius=16,
        start_text="Clique pour lancer la mise en prod.",
        timing_text="Respire profondément, et clique\nquand 15 sec se sont écoulées",
        target: float = 15.0,  # seconds
        on_complete=None,
        **kwargs
    ):
        super().__init__(**kwargs)

        # Appearance
        self.border_color = border_color
        self.border_radius = border_radius
        self.start_text = start_text
        self.timing_text = timing_text
        self.target = target
        self.on_complete = on_complete
        self.hovered = False

        # State
        self.state = "ready"   # ready → timing → finished
        self._start_time: float | None = None
        self.result_time: float | None = None

        # Embedded text widget
        self.text_widget = TextWidget(
            self.start_text, font=FontProvider.get(("JACK.TTF", 42)),
            color=ColorProvider.get('bg_dark'), align='center', line_height_multiplier=1.2,
            rel_x=0.5, rel_y=0.5, rel_width=0.8, rel_height=0.1, container_rect=self.rect
        )

    def updateText(self, text: str):
        self.text_widget.text = text

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 or \
           event.type == pygame.KEYDOWN and event.unicode != "":
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self._handle_click()

    def _handle_click(self):
        if self.state == "ready":
            # Start hidden timer
            self.state = "timing"
            self._start_time = time.time()
            self.updateText(self.timing_text)

        elif self.state == "timing":
            # Second click: stop timer
            self.state = "finished"
            if self._start_time is not None:
                self.result_time = time.time() - self._start_time
            else:
                self.result_time = None

            # Let the user handle scoring / comparing against target
            if self.on_complete:
                self.on_complete()

    def update(self, dt: float):
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)
        if is_hovered != self.hovered:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if is_hovered else pygame.SYSTEM_CURSOR_ARROW)

    def draw(self, surface: pygame.Surface):
        # Color based on state
        if self.state == "ready":
            color = (50, 200, 50)   # green
        elif self.state == "timing":
            color = (200, 200, 50)  # yellow
        elif self.state == "finished":
            color = (50, 50, 200)   # blue
        else:
            return

        pygame.draw.rect(surface, color, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(surface, self.border_color, self.rect, width=3, border_radius=self.border_radius)
        self.text_widget.draw(surface)


class SequenceMemoryWidget(DrawingGrid):
    STEP_DURATION = 0.6   # how long a cell stays lit
    PAUSE_DURATION = 0.3  # pause between highlights
    START_LENGTH = 1

    def __init__(self, on_complete=None, on_step=None, **kwargs):
        super().__init__((4, 4), **kwargs)
        self.on_complete = on_complete
        self.on_step = on_step

        # State
        self.sequence: list[int] = []
        self.user_progress = 0
        self.playing_back = False
        self._play_index = 0
        self._play_timer = 0.0
        self.hovered = False

        # Start fresh
        self._new_game()

    def _new_game(self):
        """Reset game with a new sequence of length START_LENGTH."""
        self.sequence = [random.randrange(16) for _ in range(self.START_LENGTH)]
        self.user_progress = 0
        self._start_playback()

    def _extend_sequence(self):
        """Add one step and replay."""
        self.sequence.append(random.randrange(16))
        self.user_progress = 0
        self.on_step()
        self._start_playback()

    def _start_playback(self):
        self.playing_back = True
        self._play_index = 0
        self._play_timer = -0.6
        if self.hovered:
            self.hovered = False
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)
        
        for cell in self.cells:
            cell.filled_color = ColorProvider.get('fg2')
        self.clear()
        
    def _fail(self):
        if self.on_complete:
            self.on_complete()
        # self._new_game()

    def handle_event(self, event: pygame.event.Event):
        if self.playing_back:
            return

        if event.type == pygame.MOUSEMOTION:
            is_hovered = not self.playing_back and any(cell.rect.collidepoint(pygame.mouse.get_pos()) for cell in self.cells)
            if is_hovered != self.hovered:
                self.hovered = is_hovered
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if is_hovered else pygame.SYSTEM_CURSOR_ARROW)
        
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            pos = event.pos
            for idx, cell in enumerate(self.cells):
                if cell.rect.collidepoint(pos):
                    self._handle_click(idx)
                    cell.color.animate(ColorProvider.get('fg'), end=cell.empty_color, duration=0.5, easing=ease_in_out)
                    

    def _handle_click(self, idx: int) -> bool:
        expected = self.sequence[self.user_progress]
        if idx == expected:
            self.user_progress += 1
            if self.user_progress == len(self.sequence):
                self._extend_sequence()
        else:
            self._fail()

    def update(self, dt: float):
        super().update(dt)

        if self.playing_back:
            self._play_timer += dt
            if self._play_timer >= self.STEP_DURATION + self.PAUSE_DURATION:
                # move to next step
                self._play_timer = 0.0
                self._play_index += 1
                self.clear()

                if self._play_index >= len(self.sequence):
                    self.playing_back = False
                    for cell in self.cells:
                        cell.filled_color = ColorProvider.get('fg')
            else:
                if 0 < self._play_timer < self.STEP_DURATION:
                    idx = self.sequence[self._play_index]
                    for i, c in enumerate(self.cells):
                        c.set_filled(i == idx)
                else:
                    self.clear()