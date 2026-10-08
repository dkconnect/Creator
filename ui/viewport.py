"""Letterboxed, DPI-safe viewport for Creator's 1200x900 UI.

The board and all existing clickable rectangles remain in virtual coordinates.
"""
import ctypes
import sys
import pygame


_active_viewport = None


def active_mouse_pos():
    return _active_viewport.mouse_pos() if _active_viewport else pygame.mouse.get_pos()


class Viewport:
    def __init__(self, width=1200, height=900):
        global _active_viewport
        _active_viewport = self
        self.virtual_width = width
        self.virtual_height = height
        self.window_size = (width, height)
        self.scale = 1.0
        self.offset = (0, 0)

    def initial_size(self):
        # SDL desktop resolution is in the same coordinate system as set_mode.
        info = pygame.display.Info()
        # Reserve space for Windows decorations and taskbar. Use 90% as a
        # conservative initial fit; user can maximize/resize afterward.
        factor = min(1.0, info.current_w * .94 / self.virtual_width,
                     info.current_h * .86 / self.virtual_height)
        size = (max(640, int(self.virtual_width * factor)),
                max(480, int(self.virtual_height * factor)))
        self.resize(size)
        return size

    def resize(self, window_size):
        self.window_size = window_size
        w, h = window_size
        self.scale = min(w / self.virtual_width, h / self.virtual_height)
        draw_w = round(self.virtual_width * self.scale)
        draw_h = round(self.virtual_height * self.scale)
        self.offset = ((w - draw_w) // 2, (h - draw_h) // 2)

    def to_virtual(self, pos):
        x = (pos[0] - self.offset[0]) / self.scale
        y = (pos[1] - self.offset[1]) / self.scale
        if not (0 <= x < self.virtual_width and 0 <= y < self.virtual_height):
            return None
        return (int(x), int(y))

    def mouse_pos(self):
        return self.to_virtual(pygame.mouse.get_pos()) or (-10000, -10000)

    def translate_event(self, event):
        if not hasattr(event, 'pos'):
            return event
        pos = self.to_virtual(event.pos)
        if pos is None:
            return None
        data = dict(event.dict)
        data['pos'] = pos
        if event.type == pygame.MOUSEMOTION and 'rel' in data:
            data['rel'] = tuple(round(v / self.scale) for v in data['rel'])
        return pygame.event.Event(event.type, data)

    def present(self, canvas, window):
        window.fill((8, 16, 26))
        w = round(self.virtual_width * self.scale)
        h = round(self.virtual_height * self.scale)
        scaled = pygame.transform.smoothscale(canvas, (w, h))
        window.blit(scaled, self.offset)
