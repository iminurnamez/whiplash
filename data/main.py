from . import prepare,tools
from .states import splash, gameplay, high_scores, title_screen

def main():
    controller = tools.Control(prepare.ORIGINAL_CAPTION)
    states = {"SPLASH": splash.SplashScreen(),
                   "TITLE": title_screen.TitleScreen(),
                   "GAMEPLAY": gameplay.Gameplay(),
                   "HIGH_SCORES": high_scores.HighScores()}
    controller.setup_states(states, "SPLASH")
    controller.main()
