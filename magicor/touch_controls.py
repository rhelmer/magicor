"""
On-screen touch / mouse controls for Magicor.

Maps pointer presses on overlay buttons into the existing Controls flags.
"""
import sys
import pygame


BUTTON_UP = "up"
BUTTON_DOWN = "down"
BUTTON_LEFT = "left"
BUTTON_RIGHT = "right"
BUTTON_ACTION = "action"
BUTTON_MENU = "menu"

_TOUCH_ATTRS = {
    BUTTON_UP: "touchUp",
    BUTTON_DOWN: "touchDown",
    BUTTON_LEFT: "touchLeft",
    BUTTON_RIGHT: "touchRight",
    BUTTON_ACTION: "touchAction",
    BUTTON_MENU: "touchEscape",
}


def _wasm_touch_device():
    try:
        import platform as pw
        return bool(pw.window.eval(
            "(function(){"
            "if (navigator.maxTouchPoints > 0) return true;"
            "if ('ontouchstart' in window) return true;"
            "if (window.matchMedia"
            " && window.matchMedia('(pointer: coarse)').matches) return true;"
            "return /Android|webOS|iPhone|iPad|iPod|Tablet|Mobile/i"
            ".test(navigator.userAgent);"
            "})()"
        ))
    except Exception:
        return False


def _desktop_touch_device():
    try:
        touch = pygame._sdl2.touch
        if touch.get_numtouch_devices() > 0:
            return True
    except (AttributeError, NotImplementedError, pygame.error):
        pass
    return False


def prefer_touch_controls():
    if sys.platform == "emscripten":
        return _wasm_touch_device()
    return _desktop_touch_device()


def resolve_touch_controls(config):
    if "touch_controls" not in config:
        return prefer_touch_controls()
    return config.getBool("touch_controls")


class TouchControls(object):
    LOGICAL_SIZE = (800, 600)

    def __init__(self, screen):
        self.screen = screen
        self.held = set()
        self.pressed = set()
        if not pygame.font.get_init():
            pygame.font.init()
        self._font = pygame.font.SysFont(None, 22)
        self._overlay = pygame.Surface(self.LOGICAL_SIZE, pygame.SRCALPHA)
        self._layout = self._build_layout()
        self._button_rects = {name: rect for name, rect, _ in self._layout}

    def _build_layout(self):
        pad = 60
        arm_gap = 22
        cx, cy = 96, 504
        half = pad // 2
        action_r = pygame.Rect(700, 488, 84, 84)
        menu_r = pygame.Rect(714, 16, 70, 44)
        return [
            (BUTTON_UP, pygame.Rect(cx - half, cy - pad - arm_gap, pad, pad), "^"),
            (BUTTON_DOWN, pygame.Rect(cx - half, cy + arm_gap, pad, pad), "v"),
            (BUTTON_LEFT, pygame.Rect(cx - pad - arm_gap, cy - half, pad, pad), "<"),
            (BUTTON_RIGHT, pygame.Rect(cx + arm_gap, cy - half, pad, pad), ">"),
            (BUTTON_ACTION, action_r, "A"),
            (BUTTON_MENU, menu_r, "menu"),
        ]

    def _game_pos(self, pos):
        x, y = pos
        w, h = self.screen.get_size()
        lw, lh = self.LOGICAL_SIZE
        if w != lw or h != lh:
            x = int(x * lw / w)
            y = int(y * lh / h)
        return x, y

    def _button_at(self, pos):
        x, y = self._game_pos(pos)
        point = (x, y)
        for name, rect in self._button_rects.items():
            if rect.collidepoint(point):
                return name
        return None

    def _press_button(self, button):
        if button in (BUTTON_ACTION, BUTTON_MENU):
            self.pressed.add(button)
        else:
            self.held.add(button)

    def _pointer_pos(self, event=None):
        if sys.platform == "emscripten":
            try:
                import json
                import platform as pw
                raw = pw.window.eval("JSON.stringify(__magicorPointer||null)")
                if raw != "null":
                    point = json.loads(raw)
                    return int(point["x"]), int(point["y"])
                if event is not None and event.type in (
                        pygame.FINGERDOWN, pygame.FINGERUP, pygame.FINGERMOTION):
                    raw = pw.window.eval(
                        "JSON.stringify(magicor_norm_to_game(%s,%s))"
                        % (event.x, event.y))
                    if raw != "null":
                        point = json.loads(raw)
                        return int(point["x"]), int(point["y"])
            except Exception:
                pass
            if event is not None and hasattr(event, "pos"):
                return self._game_pos(event.pos)
            return None
        if event is not None and event.type in (
                pygame.FINGERDOWN, pygame.FINGERUP, pygame.FINGERMOTION):
            return (int(event.x * self.LOGICAL_SIZE[0]),
                    int(event.y * self.LOGICAL_SIZE[1]))
        if event is not None and hasattr(event, "pos"):
            return self._game_pos(event.pos)
        return None

    def _handle_pointer_down(self, pos):
        button = self._button_at(pos)
        if button:
            self._press_button(button)
            return True
        return False

    def handle_event(self, event):
        if sys.platform == "emscripten":
            pos = self._pointer_pos(event)
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if pos and self._handle_pointer_down(pos):
                    return True
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                self.held.clear()
                return True
            elif event.type == pygame.MOUSEMOTION and self.held:
                if pos:
                    button = self._button_at(pos)
                    if button in (BUTTON_UP, BUTTON_DOWN, BUTTON_LEFT, BUTTON_RIGHT):
                        self.held = {button}
                    elif button is None:
                        self.held.clear()
                return True
            elif event.type == pygame.FINGERDOWN:
                if pos and self._handle_pointer_down(pos):
                    return True
            elif event.type == pygame.FINGERUP:
                self.held.clear()
                return True
            elif event.type == pygame.FINGERMOTION and self.held:
                if pos:
                    button = self._button_at(pos)
                    if button in (BUTTON_UP, BUTTON_DOWN, BUTTON_LEFT, BUTTON_RIGHT):
                        self.held = {button}
                    elif button is None:
                        self.held.clear()
                return True
            return False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            button = self._button_at(event.pos)
            if button:
                self._press_button(button)
                return True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.held.clear()
            return True
        elif event.type == pygame.MOUSEMOTION and self.held:
            button = self._button_at(event.pos)
            if button in (BUTTON_UP, BUTTON_DOWN, BUTTON_LEFT, BUTTON_RIGHT):
                self.held = {button}
            elif button is None:
                self.held.clear()
            return True
        elif event.type in (pygame.FINGERDOWN, pygame.FINGERUP, pygame.FINGERMOTION):
            x = int(event.x * self.LOGICAL_SIZE[0])
            y = int(event.y * self.LOGICAL_SIZE[1])
            if event.type == pygame.FINGERDOWN:
                button = self._button_at((x, y))
                if button:
                    self._press_button(button)
                    return True
            elif event.type == pygame.FINGERUP:
                self.held.clear()
                return True
            elif event.type == pygame.FINGERMOTION and self.held:
                button = self._button_at((x, y))
                if button in (BUTTON_UP, BUTTON_DOWN, BUTTON_LEFT, BUTTON_RIGHT):
                    self.held = {button}
                elif button is None:
                    self.held.clear()
                return True
        return False

    def sync(self, controls):
        controls.touchUp = BUTTON_UP in self.held
        controls.touchDown = BUTTON_DOWN in self.held
        controls.touchLeft = BUTTON_LEFT in self.held
        controls.touchRight = BUTTON_RIGHT in self.held
        controls.touchAction = BUTTON_ACTION in self.pressed
        controls.touchEscape = BUTTON_MENU in self.pressed

    def end_frame(self):
        self.pressed.clear()

    def draw(self, screen):
        self._overlay.fill((0, 0, 0, 0))
        for name, rect, label in self._layout:
            active = name in self.held
            fill = (120, 190, 255, 190) if active else (30, 55, 90, 150)
            border = (180, 220, 255, 220) if active else (90, 130, 180, 180)
            if name == BUTTON_ACTION:
                pygame.draw.ellipse(self._overlay, fill, rect)
                pygame.draw.ellipse(self._overlay, border, rect, 2)
            else:
                pygame.draw.rect(self._overlay, fill, rect, border_radius=10)
                pygame.draw.rect(self._overlay, border, rect, 2, border_radius=10)
            text = self._font.render(label, True, (230, 245, 255))
            tx = rect.centerx - text.get_width() // 2
            ty = rect.centery - text.get_height() // 2
            self._overlay.blit(text, (tx, ty))
        screen.blit(self._overlay, (0, 0))
