from ui.menu_state import MenuState


def test_help_and_error_reset():
    state = MenuState()
    state.show_help = True
    state.status_message = 'Connection unavailable'
    state.reset()
    assert not state.show_help
    assert state.status_message == ''


def test_initial_menu_has_no_error_or_help():
    state = MenuState()
    assert state.current_state == MenuState.MODE_SELECT
    assert state.status_message == ''
    assert state.show_help is False


def test_renderer_help_and_join_status():
    import pytest
    pygame = pytest.importorskip('pygame')
    pygame.init()
    screen = pygame.display.set_mode((1200, 900))
    from ui.menu_renderer import MenuRenderer
    state = MenuState()
    state.show_help = True
    renderer = MenuRenderer(screen, state)
    renderer.draw()
    assert 'MODE_AI' in renderer.buttons
    state.show_help = False
    state.current_state = MenuState.ROOM_JOIN
    state.status_message = 'Cannot connect to server'
    renderer.draw()
    pygame.quit()
