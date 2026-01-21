from tkinter import Tk, DoubleVar
from common import Emplacement, Joueur, Tour, Selecteur_Carte, Entite, Game, CARTES
from time import time

def main():
    """
    Initialize and start the game.
    Creates the main window, sets up players with initial towers and resources,
    and starts the game loop.
    """
    window = Tk()
    
    player = Joueur(
        tour_roi=Tour(pos=(6, 18), width=3, height=3, is_friendly=True, emplacement=[]),
        tour_princesse_gauche=Tour(pos=(1, 17), is_friendly=True, emplacement=[]),
        tour_princesse_droite=Tour(pos=(12, 17), is_friendly=True, emplacement=[]),
        cartes=CARTES,
        elixir=DoubleVar(window, value=7),
        raw_elixir=7,
        max_elixir=10,
        trophes=100,
        selected_card=None,
    )
    
    adv = Joueur(
        tour_roi=Tour(pos=(6, 0), height=3, width=3, emplacement=[]),
        tour_princesse_gauche=Tour(pos=(1, 2), emplacement=[]),
        tour_princesse_droite=Tour(pos=(12, 2), emplacement=[]),
        cartes=CARTES,
        elixir=DoubleVar(window, value=7),
        raw_elixir=7,
        max_elixir=10,
        trophes=100,
        selected_card=None,
    )
    
    game = Game(
        player=player,
        adv=adv,
        cells=[],
        window=window,
        tick_rate=1000,
        elixir_gain=1,
        width=15,
        height=21,
        living_entities=[],
        timer = 200
    )
    
    game.draw(time())

if __name__ == "__main__":
    main()