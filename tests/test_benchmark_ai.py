import csv
import json
from pathlib import Path

import pytest

from benchmark_ai import main, play_game


def make_pattern(tmp_path):
    path = tmp_path / 'sample.json'
    path.write_text(json.dumps({'name': 'sample', 'size': 2, 'grid': [[1, 1], [1, 1]]}), encoding='utf-8')
    return path


def test_benchmark_keeps_game_unfinished_at_horizon(tmp_path):
    result = play_game(make_pattern(tmp_path), 'basic', 'learning', 57, 'BLUE', 2)
    assert result['status'] == 'UNFINISHED'
    assert result['winner'] == ''
    assert result['turns_played'] == 2
    assert result['blue_agent'] == 'basic'
    assert result['red_agent'] == 'learning'
    assert len(result['dice_sequence'].split('-')) == 2


def test_paired_starters_have_identical_dice_sequence(tmp_path):
    path = make_pattern(tmp_path)
    blue = play_game(path, 'basic', 'learning', 57, 'BLUE', 4)
    red = play_game(path, 'basic', 'learning', 57, 'RED', 4)
    assert blue['dice_sequence'] == red['dice_sequence']
    assert blue['starter'] != red['starter']


def test_cli_writes_paired_csv(tmp_path):
    path = make_pattern(tmp_path)
    output = tmp_path / 'results.csv'
    main(['--patterns', str(path.parent), '--agents', 'basic', '--turns', '2', '--games-per-pattern', '2', '--output', str(output)])
    with output.open(newline='', encoding='utf-8') as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 2
    assert {r['starter'] for r in rows} == {'BLUE', 'RED'}


def test_advanced_ai_works_with_external_dice(tmp_path):
    result = play_game(make_pattern(tmp_path), 'advanced', 'basic', 99, 'BLUE', 1)
    assert result['turns_played'] == 1
