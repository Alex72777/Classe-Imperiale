from dataclasses import dataclass
from tkinter import Button, Frame, Label, DoubleVar, Tk, ttk
from time import time
from math import floor
from random import choice, randint

@dataclass
class Carte:
    """
    Represents a card in the game with its attributes.
    
    Attributes:
        nom (str): Name of the card
        cout (int): Elixir cost to play the card
        vitesse (float): Movement speed of the unit
        nombre (int): Number of units spawned
        dps (int): Damage per second
        attaque_range (float): Attack range of the unit
        vie (int): Health points of the unit
    """
    nom: str
    cout: int
    vitesse: float
    nombre: int
    dps: int
    attaque_range: float
    vie: int

CARTES = [
    Carte(nom="Mini P.E.K.K.A",
          cout=4,
          vitesse=1,
          nombre=1,
          dps=200,
          attaque_range=1,
          vie=300,
        ),
    Carte(nom="Gargouilles",
          cout=2,
          vitesse=1,
          nombre=1,
          dps=80,
          attaque_range=1,
          vie=300,
        ),
    Carte(nom="Barbares",
          cout=3,
          vitesse=1,
          nombre=1,
          dps=100,
          attaque_range=1,
          vie=300,
        ),
    Carte(nom="Valkyrie",
          cout=5,
          vitesse=1,
          nombre=1,
          dps=120,
          attaque_range=1,
          vie=300,
        ),
    Carte(nom="Chevaucheur de cochon",
          cout=4,
          vitesse=1,
          nombre=1,
          dps=150,
          attaque_range=1,
          vie=300,
        ),
    Carte(nom="Archères",
          cout=2,
          vitesse=1,
          nombre=1,
          dps=100,
          attaque_range=1,
          vie=300,
        ),
]

@dataclass(init=False)
class Entite:
    """
    Represents a game entity (unit) on the board.
    
    Attributes:
        pos_x (int): X position on the board
        pos_y (int): Y position on the board
        is_friendly (bool): True if entity belongs to player
        carte (Carte): Card object that created this entity
        vie (int): Current health points
        dps (int): Damage per second
    """
    def __init__(self,
                pos_y: int,
                pos_x: int,
                is_friendly: bool,
                carte: Carte,):
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.is_friendly = is_friendly
        self.carte = carte
        self.vie = carte.vie
        self.dps = carte.dps
        self.nombre = carte.nombre
        
    def next_move(self, cells) -> "Emplacement":
        """Calculate next movement position based on current position and allegiance."""
        height = len(cells[0])
        if self.is_friendly:
            new_y = max(0, self.pos_y - 1)
        else:
            new_y = min(height - 1, self.pos_y + 1)
        return cells[new_y][self.pos_x]
    
    def goto(self, game: "Game"):
        """Move entity to next position or attack if blocked by enemy."""
        next_emplacement = self.next_move(game.cells)
        
        if not self.can_goto(next_emplacement, len(game.cells[0])):
            if next_emplacement.pris_par and next_emplacement.pris_par.is_friendly != self.is_friendly:
                self.attack(next_emplacement.pris_par)
            return
        
        current_cell: Emplacement = game.get_cell(self.pos_x, self.pos_y)
        current_cell.empty()    
        
        next_emplacement.pris_par = self
        self.pos_y = next_emplacement.y
        next_emplacement.configure(
            text=self.carte.nom[0],
            bg='purple' if self.is_friendly else 'orange'
        )
    
    def can_goto(self, emplacement: "Emplacement", height: int) -> bool:
        """Check if entity can move to specified position."""
        if (0 <= emplacement.y < height and 
                    not emplacement.pris_par and 
                    not emplacement.is_water):
            return True
        return False
    
    def attack(self, entity: "Entite | Tour"):
        """Perform attack on another entity or tower."""
        # print(f"{self.carte.nom} ({self.vie}) friendly: {self.is_friendly} attacks {entity.carte.nom if isinstance(entity, Entite) else "Tour"} ({entity.vie})")
        entity.vie = max(0, entity.vie - self.dps * self.nombre)
    
    @property
    def is_alive(self) -> bool:
        if self.vie > 0:
            return True
        return False

@dataclass
class Tour:
    """
    Represents a tower structure in the game.
    
    Attributes:
        pos (tuple): (x,y) position of tower
        emplacement (list[Emplacement]): Grid cells occupied by tower
        vie (int): Tower health points
        degats (int): Tower damage
        width (int): Tower width in cells
        height (int): Tower height in cells
        is_friendly (bool): True if tower belongs to player
    """
    pos: tuple
    emplacement: "list[Emplacement]"
    vie: int = 2000
    degats: int = 10
    width: int = 2
    height: int = 2
    is_friendly: bool = False

@dataclass(init=False)
class Emplacement(Button):
    """
    Represents a cell on the game board.
    
    Attributes:
        pris_par (Tour | Entite | None): Entity occupying this cell
        x (int): X position on board
        y (int): Y position on board
        is_water (bool): True if cell is water/river
        colour (str): Background color of cell
    """
    pris_par: Tour | Entite | None = None
    x: int
    y: int
    is_water: bool
    colour: str
    
    @property
    def base_colour(self) -> str:
        return self.base_colour
    
    @base_colour.setter
    def base_colour(self, colour):
        self.colour = colour
        self.configure(bg=colour)
    
    def empty(self):
        self.pris_par = None
        self.configure(bg=self.colour, text='')
    
@dataclass(init=False)
class Selecteur_Carte(Button):
    carte: Carte

@dataclass
class Joueur:
    """
    Represents a player in the game.
    
    Attributes:
        tour_roi (Tour): Player's king tower
        tour_princesse_gauche (Tour): Left princess tower
        tour_princesse_droite (Tour): Right princess tower
        cartes (list[Carte]): Player's deck of cards
        raw_elixir (float): Current elixir amount
        elixir (DoubleVar): Tkinter variable for elixir display
        max_elixir (int): Maximum elixir capacity
        trophes (int): Player's trophy count
        selected_card (Selecteur_Carte | None): Currently selected card
    """
    tour_roi: Tour
    tour_princesse_gauche: Tour
    tour_princesse_droite: Tour
    cartes: list[Carte]
    raw_elixir: float
    elixir: DoubleVar
    max_elixir: int
    trophes: int
    selected_card: Selecteur_Carte | None
    
    @property
    def cout_moyen(self) -> float:
        somme = 0
        for i in range(len(self.cartes)):
            somme += self.cartes[i].cout
        return round(somme / len(self.cartes), 1)
    
    def prendre_carte(self, selecteur_carte: Selecteur_Carte):
        if self.selected_card:
            self.selected_card['bg'] = "grey"
        
        self.selected_card = selecteur_carte
        self.selected_card.carte = selecteur_carte.carte
        self.selected_card['bg'] = "yellow"
    
    def place_card(self, emplacement: Emplacement, game: "Game"):
        if not self.selected_card:
            return
        
        if emplacement.pris_par or emplacement.is_water:
            return
        
        if self.raw_elixir >= self.selected_card.carte.cout:
            new_entity = Entite(emplacement.y,
                                emplacement.x,
                                is_friendly=True,
                                carte=self.selected_card.carte,)
            game.add_entity(self, game.get_cell(new_entity.pos_x, new_entity.pos_y), new_entity)
            
            

@dataclass
class Game:
    """
    Main game class handling game state and logic.
    
    Attributes:
        player (Joueur): Player object
        adv (Joueur): Opponent object
        cells (list[list[Emplacement]]): Game board grid
        window (Tk): Tkinter window
        tick_rate (int): Game update interval in ms
        elixir_gain (float): Elixir gained per second
        width (int): Board width
        height (int): Board height
        living_entities (list[Entite]): Active entities on board
        timer (int): Game timer
    """
    player: Joueur
    adv: Joueur
    cells: list[list[Emplacement]]
    window: Tk
    tick_rate: int
    elixir_gain: float # per s
    width: int
    height: int
    living_entities: list[Entite]
    timer: int
    
    def add_entity(self, summoner: Joueur, emplacement: Emplacement, entity: Entite):
        if emplacement.pris_par: return
        self.get_cell(entity.pos_x, entity.pos_y).configure(text=entity.carte.nom[0], bg="purple" if entity.is_friendly else "orange")
        summoner.raw_elixir = summoner.raw_elixir - entity.carte.cout
        if summoner.selected_card: summoner.selected_card['bg'] = "grey"
        self.selected_card = None
        emplacement.pris_par = entity
        self.living_entities.append(entity)
    
    def get_cell(self, pos_x, pos_y) -> Emplacement:
        return self.cells[pos_y][pos_x]
        
    def draw(self, last_tick):
        player = self.player
        adv = self.adv
        window = self.window
        
        Label(window, text=f"Joueur - Trophés: {player.trophes}, Coût moyen(Elixir): {player.cout_moyen}").pack()
        
        game_tab = Frame(window, padx=10, pady=10)
        game_tab.pack()
        
        width, height = self.width, self.height
        tab = []
        for i in range(width):
            tab.append([])
            for y in range(height):
                btn = Emplacement(game_tab, width=3, height=1, border=0)
                btn.base_colour = 'springgreen3'
                btn.is_water = False
                btn.x, btn.y = i, y
                btn['command'] = lambda btn = btn, game = self: player.place_card(emplacement=btn, game=game)
                if (i + y) % 2: btn.base_colour = 'springgreen2'
                tab[i].append(btn)
                btn.grid(row=y, column=i)
        
        # water
        water_width, water_height = width, 3
        for i in range(water_width):
            for y in range(water_height):
                tab[i][int(height / 2) + y - 1].base_colour = "royalblue1"
                tab[i][int(height / 2) + y - 1].is_water = True
        
        # paths vertical
        bridge_width, bridge_height, space_from_walls, bridge_colour = 2, 3, 1, 'tan4'
        path_width, path_colours = bridge_width, ['darkolivegreen2', 'darkolivegreen3']
        for i in range(path_width):
            for y in range(height - 4):
                tab[i + space_from_walls][y + 2].base_colour = path_colours[0]
                tab[-(i + 1 + space_from_walls)][y + 2].base_colour = path_colours[0]
                if not (i + y) % 2:
                    tab[-(i + 1 + space_from_walls)][y + 2].base_colour = path_colours[1]
                else:
                    tab[i + space_from_walls][y + 2].base_colour = path_colours[1]
        
        # bridges
        for i in range(bridge_width):
            for y in range(bridge_height):
                tab[i + space_from_walls][int(height / 2) + y - 1].base_colour = bridge_colour
                tab[i + space_from_walls][int(height / 2) + y - 1].is_water = False
                tab[-(i + 1 + space_from_walls)][int(height / 2) + y - 1].base_colour = bridge_colour
                tab[-(i + 1 + space_from_walls)][int(height / 2) + y - 1].is_water = False
        
        # Towers
        
        towers = [
            player.tour_roi,
            player.tour_princesse_gauche,
            player.tour_princesse_droite,
            adv.tour_roi,
            adv.tour_princesse_gauche,
            adv.tour_princesse_droite
        ]
        
        for tour in towers:
            for x in range(tour.pos[1], tour.pos[1] + tour.width):
                for y in range(tour.pos[0], tour.pos[0] + tour.height):
                    emplacement: Emplacement = tab[y][x]
                    emplacement['bg'] = "blue3" if tour.is_friendly else "red3"
                    emplacement.pris_par = tour
                    tour.emplacement.append(emplacement)
        
        self.cells = tab
        
        deck = Frame(self.window, padx=10)
        for i in range(5):
            carte = choice(CARTES)
            Label(deck, text=carte.cout).grid(column=i, row=0)
            btn = Selecteur_Carte(deck, width=8, height=4, bg="grey", text=carte.nom)
            btn.carte = carte
            btn['command'] = lambda btn = btn: player.prendre_carte(btn)
            btn.grid(column=i, row=1)
        deck.pack()    
        
        Label(window, text="Elixir", pady=5).pack()
        
        elix_frame = Frame(window, pady=5)
        elix_frame.pack()
        
        current_elixir = Label(elix_frame, textvariable=player.elixir)
        current_elixir.grid(column=0)
        
        elixir = ttk.Progressbar(elix_frame, length=300, variable=player.elixir, maximum=player.max_elixir)
        elixir.grid(column=1, row=0)
        
        max_elixir = Label(elix_frame, text=player.max_elixir)
        max_elixir.grid(column=2, row=0)
        
        self.tick(last_tick)
        window.mainloop()
    
    def tick(self, last_tick):
        current_time = time()
        dt = current_time - last_tick
        last_tick = current_time
        TICK_RATE = self.tick_rate  # ms
        ELIXIR_GAIN = self.elixir_gain  # elixir per s
        player = self.player
        adv = self.adv
        tab = self.cells
        window = self.window

        # Update elixir
        player.raw_elixir = min(player.raw_elixir + ELIXIR_GAIN * dt, player.max_elixir)
        adv.raw_elixir = min(adv.raw_elixir + ELIXIR_GAIN * dt, adv.max_elixir)
        player.elixir.set(floor(player.raw_elixir))
        
        tours = [
            player.tour_roi,
            player.tour_princesse_gauche,
            player.tour_princesse_droite,
            adv.tour_roi,
            adv.tour_princesse_gauche,
            adv.tour_princesse_droite,
        ]
        
        # Update entities
        for entity in self.living_entities:
            entity.goto(self)
        
        for entity in self.living_entities:
            if not entity.is_alive:
                x, y = entity.pos_x, entity.pos_y
                self.get_cell(x, y).empty()
                self.living_entities.pop(self.living_entities.index(entity))
        
        for tour in tours:
            pass
        
        print(adv.raw_elixir)
        ### Enemy logic ###
        card = choice(adv.cartes)
        if adv.raw_elixir >= card.cout:
            left_or_right = randint(1, 100)
            new_entity = Entite(8, 12, False, card)
            if left_or_right > 50:
                new_entity.pos_x = 2
            else:
                new_entity.pos_y = self.width - 2
            self.add_entity(adv, self.get_cell(new_entity.pos_x, new_entity.pos_y), new_entity)
    
        window.after(TICK_RATE, lambda: self.tick(last_tick))