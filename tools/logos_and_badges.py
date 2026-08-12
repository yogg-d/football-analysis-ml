from PIL import Image, ImageEnhance
import requests
from io import BytesIO
import matplotlib.cm as cm

def get_competition_logo(competition, year=None, logo_brighten=False):
  url = None

    if competition in ['EPL', 'Premier League', 'GB1']:
        url = ("https://static.sport.optus.com.au/images/competition/PL.png" if logo_brighten else
               "https://www.fifplay.com/img/public/premier-league-2-logo.png")

    if competition in ['EFLC', 'EFL Championship', 'Championship', 'GB2']:
        url = "https://brandlogos.net/wp-content/uploads/2022/07/efl_championship-logo_brandlogos.net_e58ej.png"

    if competition in ['EFL1', 'EFL League One', 'League One', 'GB3']:
        url = "https://a3.espncdn.com/combiner/i?img=%2Fi%2Fleaguelogos%2Fsoccer%2F500%2F25.png"

    if competition in ['EFL2', 'EFL League Two', 'League Two', 'GB4']:
        url = "https://a4.espncdn.com/combiner/i?img=%2Fi%2Fleaguelogos%2Fsoccer%2F500%2F26.png"

    if competition in ['SPL', 'Scottish Premier League', 'Scotland Premier League', 'SC1']:
        url = "https://static.wikia.nocookie.net/logopedia/images/1/16/CinchPremiership.png/"

    if competition in ['La Liga', 'La_Liga', 'La Liga Santander', 'ES1']:
        url = "https://assets.laliga.com/assets/logos/laliga-v/laliga-v-1200x1200.png"

    if competition in ['Bundesliga', 'Fußball-Bundesliga', 'Fußball Bundesliga', '1 Bundesliga', '1. Bundesliga', 'L1']:
        url = "https://1000logos.net/wp-content/uploads/2020/09/Bundesliga-Logo.png"

    if competition in ['Serie A', 'Serie_A', 'Serie A TIM', 'Lega Serie A', 'IT1']:
        url = "https://1000logos.net/wp-content/uploads/2021/10/Italian-Serie-A-logo.png"

    if competition in ['Ligue 1', 'Ligue_1', 'Ligue 1 Uber Eats', 'FR1']:
        url = "https://sportivka.net/wp-content/uploads/2021/10/Ligue_1_logo_PNG1.png"

    if competition in ['UEFA Champions League', 'Champions League', 'UCL']:
        url = "https://logoeps.com/wp-content/uploads/2013/06/uefa-champions-league-eps-vector-logo.png"

    if competition in ['World_Cup', 'World Cup', 'FIFA World Cup']:
        if year == '2022':
            url = "https://logodownload.org/wp-content/uploads/2018/07/world-cup-2022-logo-1.png"
        if year == '2018':
            url = "https://purepng.com/public/uploads/large/purepng.com-world-cup-russia-2018-fifa-pocal-logofifawmworld-cupsoccer2018footballfussballpocalsport-31528992075ouo57.png"
          
    response = requests.get(url)
    img = Image.open(BytesIO(response.content))
    img = img.crop(img.getbbox())
    width, height = img.size


"""Functions
---------
get_competition_logo(competition)
    Get URL of competition logo for competition of choice, and format image ready for printing

get_team_badge_and_colour(team, hoa='home' )
    Get team colourmap and get URL of badge image for team of choice, and format image ready for printing.
"""
