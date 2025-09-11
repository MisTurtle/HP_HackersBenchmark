import random
import pygame
import hb_utils.factories

from abc import ABC, abstractmethod
from typing import Callable, Dict, Optional, Tuple, List, Union
from hb_utils.animations import AnimatedValue
from hb_utils.maths import auto_width, lerp, ease_in_out

class Widget(ABC):

    def __init__(self, container_rect: Union[pygame.Rect, None] = None, rel_x=0, rel_y=0, rel_width=1, rel_height=1):
        """
        Base Widget class. Relative position is anchored to the widget's center
        """
        self.container_rect = container_rect if container_rect is not None else pygame.display.get_surface().get_rect()
        self.rel_x = AnimatedValue(rel_x)
        self.rel_y = AnimatedValue(rel_y)
        self.rel_width = AnimatedValue(rel_width)
        self.rel_height = AnimatedValue(rel_height)
        self.zoom = AnimatedValue(1.0)

    def update(self, dt):
        self.rel_x.update(dt)
        self.rel_y.update(dt)
        self.rel_width.update(dt)
        self.rel_height.update(dt)
        self.zoom.update(dt)

    @property
    def rect(self):
        width = int(self.rel_width.value * self.container_rect.width)
        height = int(self.rel_height.value * self.container_rect.height)
        x = self.container_rect.x + int(self.rel_x.value * self.container_rect.width) - width / 2
        y = self.container_rect.y + int(self.rel_y.value * self.container_rect.height) - height / 2
        return pygame.Rect(x, y, width, height)

    @abstractmethod
    def draw(self, surface: pygame.Surface):
        pass

    def handle_event(self, event: pygame.event.Event):
        pass


class AbstractButton(Widget, ABC):
    def __init__(self, hover_scale: float = 1.08, animate_hover=True, **kwargs):
        super().__init__(**kwargs)
        self.hovered = False
        self.clicked = False
        self.hover_scale = hover_scale
        self.animate_hover = animate_hover

    def on_click(self):
        if not self.clicked:
            return
        self.clicked = False
        self._click()

    @abstractmethod
    def _click(self):
        pass

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(pygame.mouse.get_pos()):
                self.clicked = True
                self.rel_width.animate(self.rel_width.value, self.rel_width.original_value, 0.05, after=self.on_click)
                self.rel_height.animate(self.rel_height.value, self.rel_height.original_value, 0.05)
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_ARROW)

    def update(self, dt):
        super().update(dt)
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)
        if is_hovered != self.hovered:
            pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if is_hovered else pygame.SYSTEM_CURSOR_ARROW)
        if is_hovered != self.hovered and not self.clicked:
            self.hovered = is_hovered
            if self.animate_hover:
                target_width = self.rel_width.original_value * (self.hover_scale if self.hovered else 1.0)
                target_height = self.rel_height.original_value * (self.hover_scale if self.hovered else 1.0)
                self.rel_width.animate(self.rel_width.value, target_width, 0.1, easing=ease_in_out)
                self.rel_height.animate(self.rel_height.value, target_height, 0.1, easing=ease_in_out)


class TextButton(AbstractButton):

    def __init__(self, text: str, font_name: str, color=(255, 255, 255), border_thickness: int = 3, border_radius: int = 12, bg_color=None, callback: Optional[Callable] = None, **kwargs):
        """
        font_name: name of the font to use, will scale dynamically
        color: font and border color
        border_thickness: thickness of the rounded rectangle border
        """
        super().__init__(**kwargs)
        self.text = text
        self.font_name = font_name
        self.color = AnimatedValue(color)
        self.border_thickness = AnimatedValue(border_thickness)
        self.border_radius = AnimatedValue(border_radius)
        self.bg_color = bg_color
        self.callback = callback

    def _click(self):
        if self.callback:
            self.callback()
    
    def update(self, dt):
        super().update(dt)
        self.color.update(dt)
        self.border_thickness.update(dt)
        self.border_radius.update(dt)

    def draw(self, surface):
        rect = self.rect
        self.font = hb_utils.factories.FontProvider.get((self.font_name, int(rect.height * 0.8)))
        text_surf = self.font.render(self.text, True, self.color.value)
        text_rect = text_surf.get_rect(center=rect.center)

        if rect.width == 0:  # Auto compute width
            rect.width = text_rect.width / 0.8
            rect.left = text_rect.left + (text_rect.width - rect.width) / 2
            self.rel_width.value = self.rel_width.original_value = auto_width(self.rel_height.value, rect.size, surface.get_size())

        scaled_rect = rect.scale_by(self.zoom.value)

        # Draw background + border
        if self.bg_color is not None:
            pygame.draw.rect( surface, self.bg_color, scaled_rect, border_radius=int(self.border_radius.value) )
        pygame.draw.rect( surface, self.color.value, scaled_rect, width=int(self.border_thickness.value), border_radius=int(self.border_radius.value) )

        # Scale text and keep it centered
        scaled_text = pygame.transform.smoothscale_by(text_surf, self.zoom.value)
        scaled_text_rect = scaled_text.get_rect(center=rect.center)

        surface.blit(scaled_text, scaled_text_rect.topleft)


class ImageWidget(Widget):
    def __init__(self, image: pygame.Surface, on_click: Optional[Callable] = None, **kwargs):
        super().__init__(**kwargs)
        self._on_click = on_click
        self._hovered = False
        self.image = image
    
    def handle_event(self, event):
        if self._on_click is not None:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 or event.type == pygame.KEYDOWN and event.unicode != "":
                if self.rect.collidepoint(pygame.mouse.get_pos()):
                    self._on_click()

    def update(self, dt):
        super().update(dt)
        if self._on_click is not None:
            mouse_pos = pygame.mouse.get_pos()
            is_hovered = self.rect.collidepoint(mouse_pos)
            if is_hovered != self._hovered:
                self._hovered = is_hovered
                pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_HAND if is_hovered else pygame.SYSTEM_CURSOR_ARROW)

    def draw(self, surface):
        rect = self.rect

        new_w = int(rect.width * self.zoom.value)
        new_h = int(rect.height * self.zoom.value)

        scaled_img = pygame.transform.smoothscale(self.image, (new_w, new_h))
        scaled_rect = scaled_img.get_rect(center=rect.center)
        surface.blit(scaled_img, scaled_rect.topleft)


class TextWidget(Widget):
    def __init__(
        self,
        text: str = "",
        font: pygame.font.Font = None,
        color=(255, 255, 255),
        align="left",
        rich_text: Optional[Dict[str, dict]] = None,
        reveal_letters: bool = False,      # letter-by-letter reveal
        char_delay: float = 0.05,          # delay per character
        fade_duration: float = 0.3,        # fade duration per character
        start_color=(50, 50, 50),
        line_height_multiplier=1,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.text = text
        self.font = font
        self.color = AnimatedValue(color)
        self.align = align
        self.rich_text = rich_text or {}
        self.line_height_multiplier = line_height_multiplier

        # Reveal effect
        self.reveal_letters = reveal_letters
        self.char_delay = char_delay
        self.fade_duration = fade_duration
        self.start_color = start_color
        self._elapsed = 0.0
        self._char_times: List[float] = []

        # Callback after reveal effect
        self._after = None

        if self.reveal_letters:
            self._prepare_char_timings()

    def _prepare_char_timings(self):
        """Assign reveal times per character for letter-by-letter animation."""
        t = 0.0
        self._char_times = []
        for c in self.text:
            self._char_times.append(t)
            if c != "\n" and c != " ":
                t += self.char_delay

    def update(self, dt: float):
        super().update(dt)
        self.color.update(dt)
        if self.reveal_letters:
            self._elapsed += dt
    
    def after(self, callback):
        if not self.reveal_letters:
            callback()
        else:
            self._after = callback

    def set_font(self, font: pygame.font.Font):
        self.font = font

    def _render_char(self, char: str, idx: int) -> pygame.Surface:
        """Render a single character with optional fade-in."""
        style = self.rich_text.get(char, {})
        f = self.font
        f.set_bold(style.get("bold", False))
        f.set_italic(style.get("italic", False))
        target_color = style.get("color", self.color.value)

        if self.reveal_letters:
            start_time = self._char_times[idx]
            progress = max(0.0, min(1.0, (self._elapsed - start_time) / self.fade_duration))
            r = int(self.start_color[0] + (target_color[0] - self.start_color[0]) * progress)
            g = int(self.start_color[1] + (target_color[1] - self.start_color[1]) * progress)
            b = int(self.start_color[2] + (target_color[2] - self.start_color[2]) * progress)
            color = (r, g, b)
            if idx == len(self.text.replace(" ", "").replace("\n", "")) and progress == 1.0 and self._after is not None:
                self._after()
                self._after = None
        else:
            color = target_color
        
        surf = f.render(char, True, color)
        f.set_bold(False)
        f.set_italic(False)
        return surf
    
    def _wrap_text(self, words: list[str], max_width: int) -> list[list[str]]:
        """Wrap words into lines based on max_width."""
        lines: list[list[str]] = []
        current_line: list[str] = []
        current_width = 0
        space_width = self.font.size(" ")[0]

        for word in words:
            if word == "\n":
                lines.append(current_line)
                current_line = []
                current_width = 0
                continue

            word_width = sum(self.font.size(c)[0] for c in word)
            if current_line:
                word_width += space_width  # space before word if not first

            if current_width + word_width > max_width and current_line:
                lines.append(current_line)
                current_line = [word]
                current_width = sum(self.font.size(c)[0] for c in word)
            else:
                if current_line:
                    current_width += space_width
                current_line.append(word)
                current_width += sum(self.font.size(c)[0] for c in word)

        if current_line:
            lines.append(current_line)

        return lines

    def draw(self, surface: pygame.Surface) -> list[pygame.Surface]:
        rect = self.rect
        x0, y0 = rect.topleft
        line_height = self.font.get_linesize() * self.line_height_multiplier

        # Split text into words (preserve newlines)
        lines_raw = self.text.split("\n")
        words: list[str] = []
        for line in lines_raw:
            words.extend(line.split(" "))
            words.append("\n")

        # Wrap words based on max width
        wrapped_lines = self._wrap_text(words, rect.width)

        # Render and blit
        ss = []
        y = y0
        idx = 0
        for line_words in wrapped_lines:
            # Flatten words into characters
            line_chars: list[pygame.Surface] = []
            for word in line_words:
                if word == "\n":
                    continue
                for c in word:
                    line_chars.append(self._render_char(c, idx))
                    idx += 1
                # Add space after word
                line_chars.append(self._render_char(" ", idx))

            # Calculate alignment
            total_width = sum(s.get_width() for s in line_chars)
            if self.align == "center":
                draw_x = x0 + (rect.width - total_width) // 2
            elif self.align == "right":
                draw_x = x0 + rect.width - total_width
            else:
                draw_x = x0

            for surf in line_chars:
                scaled = pygame.transform.smoothscale_by(surf, self.zoom.value)
                scaled_rect = scaled.get_rect(topleft=(draw_x, y))
                surface.blit(scaled, scaled_rect)
                ss.append(scaled_rect)
                draw_x += surf.get_width()

            y += line_height

        return ss


class TextInputWidget(TextWidget):
    def __init__(
        self,
        text: str = "",
        font: pygame.font.Font = None,
        color=(255, 255, 255),
        align="left",
        min_length: int = 0,
        max_length: Optional[int] = None,
        has_cursor: bool = True,
        cursor_transparent_color=(0, 0, 0),
        cursor_blink_speed: float = 0.5,  # seconds
        **kwargs
    ):
        super().__init__(text=text, font=font, color=color, align=align, **kwargs)
        self.min_length = min_length
        self.max_length = max_length
        self.has_cursor = has_cursor
        self.cursor_color = AnimatedValue(color)
        self.cursor_color.animate(color, cursor_transparent_color, cursor_blink_speed, loop=True, easing=ease_in_out)
        self._on_change, self._on_submit = None, None

    def update(self, dt: float):
        super().update(dt)
        self.cursor_color.update(dt)

    def on_change(self, callback):
        self._on_change = callback
    
    def on_submit(self, callback):
        self._on_submit = callback

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if len(self.text) > 0:
                    self.text = self.text[:-1]
                    self._on_change()
            elif event.key == pygame.K_RETURN:
                if self._on_submit is not None:
                    self._on_submit()
            else:
                char = event.unicode
                if char == " " and self.text == "":
                    return  # discard leading space
                if char == "":
                    return  # Ignore modifier keys
                if self.max_length is None or len(self.text) < self.max_length:
                    self.text += char
                    self._on_change()
            if self.reveal_letters:
                self._prepare_char_timings()

    def draw(self, surface: pygame.Surface):
        if len(self.text) == 0:
            self.text = "|"
            color_cache = self.color
            self.color = self.cursor_color
            super().draw(surface)
            self.color = color_cache
            self.text = ""
        else:
            surfaces = super().draw(surface)
            bar = self.font.render("|", 1, self.cursor_color.value)
            blit_pos = surfaces[-1].left - int(bar.get_width() / 2), surfaces[-1].top
            surface.blit(bar, blit_pos)


class Timer(TextWidget):

    def __init__(self, font = None, color=(255, 255, 255), align="left", rich_text = None, reveal_letters = False, char_delay = 0.05, fade_duration = 0.3, start_color=(50, 50, 50), line_height_multiplier=1, **kwargs):
        super().__init__("0.00s", font, color, align, rich_text, reveal_letters, char_delay, fade_duration, start_color, line_height_multiplier, **kwargs)
        self._time = 0
        self._running = False

    def format(self, dur):
        return f"{dur:.2f} sec"
    
    def start(self):
        self._running = True
    
    def stop(self):
        self._running = False

    def get(self):
        return self._time
    
    def update(self, dt):
        super().update(dt)
        if self._running:
            self._time += dt
            self.text = self.format(self._time)

class GuidedTextInputWidget(TextInputWidget):
    def __init__(
        self,
        placeholder: str,
        placeholder_color=(100, 100, 100),
        on_type=None,
        on_complete=None,
        **kwargs
    ):
        super().__init__(**kwargs)
        self.placeholder = placeholder
        self.placeholder_color = placeholder_color
        self._on_type = on_type
        self._on_complete = on_complete

    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_BACKSPACE:
                if len(self.text) > 0:
                    self.text = self.text[:-1]
            else:
                char = event.unicode
                if char == "":
                    return  # ignore modifiers
                
                # only accept if it's the next expected char
                next_index = len(self.text)
                if next_index < len(self.placeholder) and char == self.placeholder[next_index]:
                    self.text += char
                    self._on_type()
                    if len(self.text) == len(self.placeholder):
                        if self._on_complete:
                            self._on_complete()
            if self.reveal_letters:
                self._prepare_char_timings()

    def draw(self, surface: pygame.Surface):
        # Draw placeholder
        text_cache, color_cache = self.text, self.color.value
        self.text, self.color.value = self.placeholder, self.placeholder_color
        TextWidget.draw(self, surface)

        self.text, self.color.value = text_cache, color_cache
        self.align = "left"
        super().draw(surface)


class BinaryDropText(TextWidget):

    MIN_DROP_SPEED = 35  # px / s
    MAX_DROP_SPEED = 200  # px / s
    MIN_FONT_SIZE = 15
    MAX_FONT_SIZE = 50
    MIN_CHAIN_SIZE = 5
    MAX_CHAIN_SIZE = 15
    _color_fg = hb_utils.factories.ColorProvider.get('fg')
    _color_bg = hb_utils.factories.ColorProvider.get('bg')
    
    def __init__(self):
        super().__init__(rel_width=0.1)
        self.__reset()
    
    def __reset(self):
        self._coefficient = random.random()
        
        font_size = self.MIN_FONT_SIZE + self._coefficient * (self.MAX_FONT_SIZE - self.MIN_FONT_SIZE)
        text_length = random.randint(self.MIN_CHAIN_SIZE, self.MAX_CHAIN_SIZE)
        speed = (self.MIN_DROP_SPEED + self._coefficient * (self.MAX_DROP_SPEED - self.MIN_DROP_SPEED))

        self.text = "\n".join([f"{random.randint(0, 1)!r}" for _ in range(text_length)])
        self.set_font(hb_utils.factories.FontProvider.get(('Code.ttf', int(font_size))))

        text_height = self.font.render("1", 1, (0, 0, 0)).get_height() * text_length * 1.1
        start_height_rel = -(text_height / self.rect.height) - 0.1

        self.rel_x.value = random.random()
        self.rel_y.animate(start_height_rel, 1 - start_height_rel, duration=(self.rect.height + text_height) / speed, after=self.__reset)
        self.rel_height.value = -start_height_rel
        
        def cc(_from, _to) -> int:
            return int(_from + (_to - _from) * self._coefficient)
        
        self.color.value = cc(self._color_bg.r, self._color_fg.r), cc(self._color_bg.g, self._color_fg.g), cc(self._color_bg.b, self._color_fg.b)

    def update(self, dt):
        if random.random() < 0.01:
            self.text = str(random.randint(0, 1)) + "\n" + self.text[:-2]
        super().update(dt)



class DrawingCell(Widget):
    COLOR_TRANSITION_DURATION = 0.5

    def __init__(
        self,
        hover_color=(200, 200, 200),
        empty_color=(30, 30, 30),
        filled_color=(255, 255, 255),
        border_color=(100, 100, 100),
        filled=False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.color = AnimatedValue(empty_color)
        self.hovered = False
        self.filled = filled

        self.hover_color = hover_color
        self.empty_color = empty_color
        self.filled_color = filled_color
        self.border_color = border_color

    def is_filled(self) -> bool:
        return self.filled

    def set_filled(self, filled: bool):
        self.filled = filled

    def invert(self):
        self.set_filled(not self.filled)

    def update(self, dt: float):
        super().update(dt)
        self.color.update(dt)

    def draw(self, surface: pygame.Surface):
        pygame.draw.rect(surface, self.color.value if not self.filled else self.filled_color, self.rect)
        pygame.draw.rect(surface, self.border_color, self.rect, width=1)


class DrawingGrid(Widget):

    def __init__( self, grid_size: tuple[int, int], **kwargs ):
        super().__init__( **kwargs, )
        self.grid_size = grid_size
        self.cells: list[DrawingCell] = []
        cell_size = 1 / self.grid_size[0]

        # Build cells
        for y in range(grid_size[1]):
            for x in range(grid_size[0]):
                cell = DrawingCell(rel_x=x / self.grid_size[0], rel_y=y / self.grid_size[1], rel_width=cell_size, rel_height=cell_size, container_rect=self.rect, filled_color=hb_utils.factories.ColorProvider.get('fg2'))
                self.cells.append(cell)

    def clear(self):
        for c in self.cells:
            c.set_filled(False)

    def compare(self, pattern: list[list[bool]]) -> bool:
        for y in range(self.grid_size[1]):
            for x in range(self.grid_size[0]):
                if self.cells[y * self.grid_size[0] + x].is_filled() != pattern[y][x]:
                    return False
        return True

    def handle_event(self, event: pygame.event.Event):
        for c in self.cells:
            c.handle_event(event)

    def update(self, dt: float):
        for c in self.cells:
            c.update(dt)

    def draw(self, surface: pygame.Surface):
        for c in self.cells:
            c.draw(surface)
