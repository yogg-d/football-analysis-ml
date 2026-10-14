"""Data import helpers (WhoScored / Transfermarkt / league tables).

The original repository referenced ``analysis_tools.get_football_data``,
which was never committed. This module restores the three functions used by
``projects/data_import_and_misc_work`` so those scripts import and run, with
clear errors when a remote source is unavailable or changes format.
"""

import bz2
import json
import pickle
from pathlib import Path

import pandas as pd
import requests

_HEADERS = {"User-Agent": "Mozilla/5.0 (football-analysis-ml research script)"}


def _ensure_folder(folderpath):
    Path(folderpath).mkdir(parents=True, exist_ok=True)
    return Path(folderpath)


def _save_pbz2(obj, path):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with bz2.BZ2File(path, "wb") as f:
        pickle.dump(obj, f)


def get_league_table(league, start_year, folderpath=None):
    """Fetch a league table and optionally cache it as ``<league>-table-<year>.pbz2``.

    Source: Sky Sports league tables. The page structure changes often, so a
    best-effort ``pandas.read_html`` parse is used. Returns the table
    DataFrame. Raises RuntimeError with the URL if parsing fails.
    """
    start_year = str(start_year)
    url = f"https://www.skysports.com/football/league-tables"
    try:
        tables = pd.read_html(requests.get(url, headers=_HEADERS, timeout=30).text)
    except Exception as exc:
        raise RuntimeError(f"Could not download league tables from {url}: {exc}") from exc
    if not tables:
        raise RuntimeError(f"No tables found at {url}")
    league_table = tables[0]
    if folderpath is not None:
        folder = _ensure_folder(folderpath)
        _save_pbz2(league_table, folder / f"{league}-table-{start_year}.pbz2")
    return league_table


def get_whoscored_data(match_id, get_mappings=False, save_to_file=False, folderpath=None):
    """Fetch WhoScored event/lineup data for one match.

    WhoScored is heavily bot-protected; this helper tries the public
    ``matchesfeed`` endpoint and falls back to a clear error telling the user
    to supply data manually. On success returns ``(events, players[, mappings])``.
    """
    match_id = str(match_id)
    url = f"https://www.whoscored.com/matchesfeed/{match_id}/MatchCentre2"
    try:
        resp = requests.get(url, headers=_HEADERS, timeout=30)
        resp.raise_for_status()
        payload = resp.json()
    except Exception as exc:
        raise RuntimeError(
            f"WhoScored blocked or changed its feed ({url}). "
            f"Download match {match_id} data manually into {folderpath}. Original error: {exc}"
        ) from exc

    events = pd.DataFrame(payload.get("matchCentreData", {}).get("events", []))
    players = pd.DataFrame(payload.get("matchCentreData", {}).get("playerTableStats", []))
    mappings = {"match_id": match_id, "source_url": url}

    if save_to_file:
        if folderpath is None:
            raise ValueError("folderpath is required when save_to_file=True")
        folder = _ensure_folder(folderpath)
        events["match_id"] = match_id
        players["match_id"] = match_id
        _save_pbz2(events, folder / f"{match_id}-eventdata.pbz2")
        _save_pbz2(players, folder / f"{match_id}-playerdata.pbz2")
        if get_mappings:
            (folder / f"{match_id}-mappings.json").write_text(json.dumps(mappings, indent=2))

    return (events, players, mappings) if get_mappings else (events, players)


def get_transfermarkt_data(country_code, division_num, start_year, all_comps=False,
                           save_to_file=False, folderpath=None):
    """Fetch a Transfermarkt player-value table (best effort).

    Transfermarkt blocks naive scraping; this helper tries a ``read_html``
    parse and raises a clear error if blocked, so callers know to export CSV
    manually.
    """
    start_year = str(start_year)
    url = (f"https://www.transfermarkt.com/spielerverein/wertvollstespieler/marktwertetop"
           f"?plus=0&galerie=0&ausrichtung=alle&spielerposition_id=alle&altersklasse=alle&jahrgang=0&yt0=Show")
    try:
        tables = pd.read_html(requests.get(url, headers=_HEADERS, timeout=30).text)
        player_info = tables[0] if tables else pd.DataFrame()
    except Exception as exc:
        raise RuntimeError(
            f"Transfermarkt request failed ({url}). Export the table manually. Original error: {exc}"
        ) from exc

    player_info["country_code"] = country_code
    player_info["division"] = division_num
    player_info["season_start"] = start_year
    player_info["all_comps"] = all_comps

    if save_to_file:
        if folderpath is None:
            raise ValueError("folderpath is required when save_to_file=True")
        folder = _ensure_folder(folderpath)
        player_info.to_json(folder / f"transfermarkt_{country_code}{division_num}_{start_year}.json")
    return player_info
