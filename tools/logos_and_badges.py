"""Logos and badges helpers.

Functions
---------
get_competition_logo(competition, year=None, logo_brighten=False)
    Download a competition logo and return a cropped PIL image.

get_team_badge_and_colour(team, hoa='home')
    Return a team's badge image (or None) plus home/away colours.
"""

from io import BytesIO

import requests
from PIL import Image, ImageEnhance

# Minimal team colour/badge table. Colours are approximate club colours;
# badge URLs are best-effort and may need updating if hosts change.
_TEAM_INFO = {
    "Arsenal": {"badge": "https://logos-world.net/wp-content/uploads/2020/06/Arsenal-Logo.png",
                "home": "#EF0107", "away": "#FDB913"},
    "Liverpool": {"badge": "https://logos-world.net/wp-content/uploads/2020/06/Liverpool-Logo.png",
                  "home": "#C8102E", "away": "#00B2A9"},
    "Man City": {"badge": "https://logos-world.net/wp-content/uploads/2020/06/Manchester-City-Logo.png",
                 "home": "#6CABDD", "away": "#1C2C5B"},
    "Chelsea": {"badge": "https://logos-world.net/wp-content/uploads/2020/06/Chelsea-Logo.png",
                "home": "#034694", "away": "#FFFFFF"},
}


def _download_image(url, timeout=15):
    response = requests.get(url, timeout=timeout)
    response.raise_for_status()
    img = Image.open(BytesIO(response.content)).convert("RGBA")
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
    return img


def get_competition_logo(competition, year=None, logo_brighten=False):
    """Download a competition logo and return a cropped PIL image."""
    url = None

    if competition in ['EPL', 'Premier League', 'GB1']:
        url = ("https://static.sport.optus.com.au/images/competition/PL.png" if logo_brighten else
               "https://www.fifplay.com/img/public/premier-league-2-logo.png")
    elif competition in ['EFLC', 'EFL Championship', 'Championship', 'GB2']:
        url = "https://brandlogos.net/wp-content/uploads/2022/07/efl_championship-logo_brandlogos.net_e58ej.png"
    elif competition in ['EFL1', 'EFL League One', 'League One', 'GB3']:
        url = "https://a3.espncdn.com/combiner/i?img=%2Fi%2Fleaguelogos%2Fsoccer%2F500%2F25.png"
    elif competition in ['EFL2', 'EFL League Two', 'League Two', 'GB4']:
        url = "https://a4.espncdn.com/combiner/i?img=%2Fi%2Fleaguelogos%2Fsoccer%2F500%2F26.png"
    elif competition in ['SPL', 'Scottish Premier League', 'Scotland Premier League', 'SC1']:
        url = "https://static.wikia.nocookie.net/logopedia/images/1/16/CinchPremiership.png/"
    elif competition in ['La Liga', 'La_Liga', 'La Liga Santander', 'ES1']:
        url = "https://assets.laliga.com/assets/logos/laliga-v/laliga-v-1200x1200.png"
    elif competition in ['Bundesliga', 'Fußball-Bundesliga', 'Fußball Bundesliga', '1 Bundesliga', '1. Bundesliga', 'L1']:
        url = "https://1000logos.net/wp-content/uploads/2020/09/Bundesliga-Logo.png"
    elif competition in ['Serie A', 'Serie_A', 'Serie A TIM', 'Lega Serie A', 'IT1']:
        url = "https://1000logos.net/wp-content/uploads/2021/10/Italian-Serie-A-logo.png"
    elif competition in ['Ligue 1', 'Ligue_1', 'Ligue 1 Uber Eats', 'FR1']:
        url = "https://sportivka.net/wp-content/uploads/2021/10/Ligue_1_logo_PNG1.png"
    elif competition in ['UEFA Champions League', 'Champions League', 'UCL']:
        url = "https://logoeps.com/wp-content/uploads/2013/06/uefa-champions-league-eps-vector-logo.png"
    elif competition in ['World_Cup', 'World Cup', 'FIFA World Cup']:
        if str(year) == '2022':
            url = "https://logodownload.org/wp-content/uploads/2018/07/world-cup-2022-logo-1.png"
        elif str(year) == '2018':
            url = "https://purepng.com/public/uploads/large/purepng.com-world-cup-russia-2018-fifa-pocal-logofifawmworld-cupsoccer2018footballfussballpocalsport-31528992075ouo57.png"

    if url is None:
        raise ValueError(f"No logo URL known for competition {competition!r}")

    img = _download_image(url)
    if logo_brighten:
        img = ImageEnhance.Brightness(img).enhance(1.2)
    return img


def get_team_badge_and_colour(team, hoa='home'):
    """Return (badge_image_or_None, colour) for a team.

    Args:
        team: team name.
        hoa: 'home' or 'away' colour selection.

    Returns:
        tuple: (PIL image or None, hex colour string). Badge download
        failures return None rather than raising, so plots never crash.
    """
    info = _TEAM_INFO.get(team, {})
    colour = info.get('away' if hoa == 'away' else 'home', '#808080')
    badge = None
    if info.get('badge'):
        try:
            badge = _download_image(info['badge'])
        except Exception:
            badge = None
    return badge, colour
