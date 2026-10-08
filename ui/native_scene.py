"""One native-resolution pass for the Creator gameplay scene.

All coordinates remain in Creator's virtual coordinate system, while the
actual rasterization occurs on the OS display surface.
"""
from ui.native_board import draw_native_board
from ui.native_hud import draw_native_hud


def draw_native_scene(window, viewport, renderer):
    if renderer is None or renderer.game.game_over:
        return
    draw_native_board(window, viewport, renderer)
    draw_native_hud(window, viewport, renderer)
