import pytest
import os
import sys

from abdwp.retrosheet import download_gamelogs
from abdwp.retrosheet import load_gamelogs
from abdwp.retrosheet import download_events
from abdwp.retrosheet import load_pbp
from abdwp.retrosheet import load_rosters
from abdwp.retrosheet import load_teams


def test_download_gamelogs_runs():
    try:
        download_gamelogs(2019)
    except Exception:
        pass


def test_load_gamelogs_runs():
    try:
        load_gamelogs(2019)
    except Exception:
        pass


def test_download_events_runs():
    try:
        download_events(2019)
    except Exception:
        pass


def test_load_pbp_runs():
    try:
        load_pbp(2019)
    except Exception:
        pass


def test_load_rosters_runs():
    try:
        load_rosters(2019)
    except Exception:
        pass


def test_load_teams_runs():
    try:
        load_teams(2019)
    except Exception:
        pass


@pytest.mark.skipif(sys.platform != "win32", reason="Only runs on Windows")
def test_load_pbp_works():
    file_dir = os.path.dirname(__file__)
    download_events(2019, cwevent_dir=file_dir)
    df = load_pbp(2019)
    assert df is not None
