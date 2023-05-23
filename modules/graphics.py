"""module de définition des classes principales"""
from dataclasses import dataclass
from typing import List, Any, Tuple, Dict, Callable
import pygame

pygame.init = pygame.init
pygame.init()

# constantes

POLICE = pygame.font.SysFont('Arial', 20)

# fonctions


def vect2_to_tuple(vecteur: pygame.Vector2):
    """convertie un vecteur2 en tuple d'entier"""
    return round(vecteur.x), round(vecteur.y)


def dichotomie(liste: List[float], valeur: float):
    """effectue une recherche dichotomique et
    renvoie l'indice s'il existe"""

    if liste == []:
        return 0

    start = 0
    end = len(liste) - 1

    while end - start > 0:
        mid = (start + end) // 2
        if liste[mid] == valeur:
            return mid
        if liste[mid] > valeur:
            end = mid
        else:
            start = mid + 1

    return start + 1 if valeur > liste[start] else start


def relpos_to_absolute(pos: 'Vector3'):
    """
    transforme une position relative à
    une frame en une position écran
    """
    return Frame.current_tl_pos.xy + pos.xy


def absolute_to_relpos(pos: 'Vector3'):
    """transforme une position
    absolue en position relative"""
    return pos.xy - Frame.current_tl_pos.xy


# classes


@dataclass
class Vector3(pygame.Vector3):
    """vecteur 3D"""

    x: float
    y: float
    z: float
    aligne: str = 'topleft'


class RelativePos:
    """
    classe de représentation
    des positions variables
    """
    default_window: pygame.Surface

    def __init__(self, relx: float, rely: float, posz: int, **args: Any) -> None:
        self.relx, self.rely = relx, rely
        self.x: float
        self.y: float
        self.z = posz
        self.aligne = args.get('aligne', 'centre')
        window = args.get('window')
        self.window = window if window is not None else RelativePos.default_window
        self.update()

    @property
    def xy(self):
        """renvoie les composantes xy du vecteur position"""
        return pygame.Vector2(self.x, self.y)

    def update(self):
        """méthode de mise à jour"""

        self.x = self.relx * self.window.get_width()
        self.y = self.rely * self.window.get_height()


class Sequence:
    """classe de gestion des séquences"""

    sequences: List['Sequence']

    def __init__(self, seq: List[Tuple[Tuple[Callable[..., None],
                                             List[Any]] | None, float]],
                 loop: bool = False, local: bool = False) -> None:

        self.seq_infos: Dict[str, Any] = {
            "fnct": [],
            "times": [],
            "is_running": False,
            "sqc_timer": pygame.time.get_ticks(),
            "pointer": 0,
            "loop": loop,
            "local": local
        }

        if self.seq_infos['local'] and not self.seq_infos['loop']:
            Sequence.sequences.append(self)

        for elm in seq:
            self.seq_infos['fnct'].append(elm[0])
            self.seq_infos['times'].append(elm[1])

    def start(self):
        """commence la séquence"""
        self.seq_infos['is_running'] = True
        self.seq_infos['pointer'] = 0
        self.seq_infos['seq_timer'] = pygame.time.get_ticks()

    def fin(self):
        """met fin à la séquence"""
        self.seq_infos['running'] = False

    def update(self):
        """met à jour la séquence"""
        if (not self.seq_infos["is_running"] or
            (self.seq_infos['times'][self.seq_infos['pointer']] >
             pygame.time.get_ticks() - self.seq_infos["sqc_timer"])):
            return False

        fnct = self.seq_infos['fnct'][self.seq_infos['pointer']]
        if fnct is not None:
            fnct[0](*fnct[1])
        self.seq_infos["pointer"] += 1
        self.seq_infos['sqc_timer'] = pygame.time.get_ticks()

        if self.seq_infos["pointer"] >= len(self.seq_infos['pointer']):
            if self.seq_infos["loop"]:
                self.start()
            else:
                self.seq_infos["is_running"] = False
        return True

    @classmethod
    def local_update(cls):
        """met à jour les séquences locales"""
        for seq in cls.sequences:
            seq.update()

        ind = 0
        while ind < len(Sequence.sequences):
            seq = Sequence.sequences[ind]
            if seq.seq_infos["pointer"] >= len(seq.seq_infos["times"]):
                seq.destroy()
            else:
                ind += 1

    def destroy(self):
        """détruit la séquence"""
        if self in Sequence.sequences:
            Sequence.sequences.remove(self)
        del self


class Interface:
    """classe de représentation des Interfaces"""
    current_interface: 'Interface'
    interfaces: Dict[str, 'Interface'] = {}

    def __init__(self, nom: str | None = None) -> None:
        self.elements: List['Element'] = []

        if nom is not None:
            self.nom = nom
            Interface.interfaces[nom] = self

    def add_element(self, element: 'Element'):
        """ajoute un élément à la liste"""
        index: int = dichotomie(
            [elm.pos.z for elm in self.elements], element.pos.z)
        self.elements.insert(index, element)
        element.elm_infos["interface"] = self

    def resort(self, element: 'Element'):
        """replace un élément"""
        self.elements.remove(element)
        index: int = dichotomie(
            [elm.pos.z for elm in self.elements], element.pos.z)
        self.elements.insert(index, element)

    def remove_element(self, element: 'Element'):
        """retire un élément de la liste"""
        self.elements.remove(element)

    def on_keypress(self, event: pygame.event.Event):
        """gère les touches appuyées"""
        for elm in self.elements:
            if hasattr(elm.elm_infos["objet"], 'on_keypress'):
                elm.elm_infos["objet"].on_keypress(event)

    def on_click(self, event: pygame.event.Event):
        """gestion des cliques"""
        for elm in self.elements[::-1]:
            if (hasattr(elm.elm_infos["objet"], 'on_click') and
                    elm.elm_infos['rect'].collidepoint(absolute_to_relpos(
                        Vector3(*pygame.mouse.get_pos(), 0)))):
                elm.elm_infos["objet"].on_click(event)
                return

    def on_declick(self, event: pygame.event.Event):
        """gestion du relachement du clique"""
        for elm in self.elements[::-1]:
            if (hasattr(elm.elm_infos["objet"], 'on_declick') and
                    elm.elm_infos['rect'].collidepoint(absolute_to_relpos(
                        Vector3(*pygame.mouse.get_pos(), 0)))):
                elm.elm_infos["objet"].on_declick(event)
                return

    def update(self):
        """mise à jour"""
        for elm in self.elements:
            if hasattr(elm.elm_infos["objet"], 'update'):
                elm.elm_infos["objet"].update()
            if hasattr(elm, 'update'):
                elm.update()

    def render(self):
        """méthode d'affichage"""
        return (elm.render() for elm in self.elements)

    @classmethod
    def add_element_to(cls, element: 'Element', interface_nom: str):
        """ajoute un élément à l'interface donnée"""
        if interface_nom in cls.interfaces:
            cls.interfaces[interface_nom].add_element(element)

    @classmethod
    def change_interface(cls, interface_nom: str):
        """change l'interface actuelle"""
        cls.current_interface = cls.interfaces[interface_nom]


class Element:
    """
    classe de représentation
    d'un élément graphique
    """

    def __init__(self, objet: Any, surface: pygame.Surface, rectangle: pygame.Rect,
                 interface_nom: str | None = None) -> None:

        self.elm_infos: Dict[str, Any] = {
            "surface": surface,
            "rect": rectangle,
            "objet": objet,
            "interface": None
        }

        self.backup_rotation = 0
        self.pos: Vector3 | RelativePos = self.elm_infos["objet"].pos

        if interface_nom is None:
            Interface.current_interface.add_element(self)
        else:
            Interface.add_element_to(self, interface_nom)

    def delink(self):
        """délie l'élément"""
        self.elm_infos["interface"].remove_element(self)

    def destroy(self):
        """détruit l'objet localement,
        sans garanti pour les duplicats"""
        self.delink()
        del self

    def ancre(self):
        """ancre le rectangle à la bonne position"""

        self.pos: Vector3 | RelativePos = self.elm_infos['objet'].pos

        ancre = self.pos.aligne  # type: ignore

        self.elm_infos['rect'].center = vect2_to_tuple(self.pos.xy)
        if 'top' in ancre:
            self.elm_infos['rect'].top = vect2_to_tuple(self.pos.xy)[1]
        elif 'bottom' in ancre:
            self.elm_infos['rect'].bottom = vect2_to_tuple(self.pos.xy)[1]
        if 'left' in ancre:
            self.elm_infos['rect'].left = vect2_to_tuple(self.pos.xy)[0]
        elif 'right' in ancre:
            self.elm_infos['rect'].right = vect2_to_tuple(self.pos.xy)[0]

    def update(self):
        """methode de mise à jour"""
        if isinstance(self.pos, RelativePos):
            self.pos.update()
        self.ancre()

        if "objet" in self.elm_infos and hasattr(self.elm_infos["objet"], 'rotation'):
            # en degrés
            self.elm_infos["surface"] = pygame.transform.rotate(
                self.elm_infos["surface"],
                self.elm_infos["objet"].rotation - self.backup_rotation)
            self.backup_rotation = self.elm_infos["objet"].rotation

    def render(self):
        """méthode d'affichage"""
        return self.elm_infos["surface"], self.elm_infos["rect"]


class Frame:
    """
    classe de représentation d'un groupement
    d'élément dans un cadre
    """

    current_frame: 'None | Frame' = None
    current_tl_pos: Vector3 = Vector3(0, 0, 0)

    frames: Dict[str, 'Frame'] = {}

    def __init__(self, interface: Interface, surface: pygame.Surface,
                 pos: 'Vector3 | RelativePos', **args: str) -> None:
        self.surface = surface
        self.backup = surface.copy()
        self.rect = self.surface.get_rect()
        self.pos = pos
        self.interface = interface
        self.element = Element(self, surface, self.rect, args.get('interface_nom'))
        nom = args.get('nom', 'sans_nom')
        if nom not in Frame.frames:
            self.nom = nom
            Frame.frames[nom] = self

    def recursive_position(self, fonction: Callable[..., Any]):
        """traque la position de manière récursive"""
        def tracer(*args: ..., **kwargs: ...):
            """trace la position"""
            # on active la frame mise à jour
            backup = Frame.current_frame
            Frame.current_frame = self
            # type: ignore
            Frame.current_tl_pos.xy += Vector3(
                *self.element.elm_infos['rect'].topleft, 0).xy

            # update
            fonction(*args, **kwargs)

            # on désactive la frame mise à jour
            Frame.current_frame = backup
            # type: ignore
            Frame.current_tl_pos.xy -= Vector3(
                *self.element.elm_infos['rect'].topleft, 0).xy
        return tracer

    def on_keypress(self, event: pygame.event.Event):
        """gestion des touches"""
        self.recursive_position(self.interface.on_keypress)(event)

    def on_click(self, event: pygame.event.Event):
        """gestion des cliques"""
        self.recursive_position(self.interface.on_click)(event)

    def on_declick(self, event: pygame.event.Event):
        """gestion du relachement des cliques"""
        self.recursive_position(self.interface.on_declick)(event)

    def destroy(self):
        """détruit la frame"""
        del Frame.frames[self.nom]
        self.element.destroy()

    def update(self):
        """méthode de mise à jour"""
        # clear
        self.surface.blit(self.backup, (0, 0))

        # update
        self.recursive_position(self.interface.update)()

        self.surface.blits(list(self.interface.render()))


class StaticElement(Element):
    """création d'un modèle immuable"""

    def __init__(self, objet: Any, surface: pygame.Surface,
                 interface_nom: str | None = None) -> None:
        super().__init__(objet, surface, surface.get_rect(), interface_nom)
        self.ancre()

    def update(self):
        """surécrit la méthode pour la désactiver"""
        return


class StaticModel:
    """gestion des éléments visuels invariables"""

    def __init__(self, surface: pygame.Surface, pos: Vector3 | RelativePos,
                 interface_nom: str) -> None:
        self.pos = pos
        self.element = StaticElement(self, surface, interface_nom)


class AnimElement(Element):
    """classe de gestion des animations"""

    def __init__(self, objet: Any, default_texture: pygame.Surface,
                 textures: Dict[str, List[Tuple[pygame.Surface, float]]],
                 interface_nom: str | None = None) -> None:
        """infos: temps en millisecondes"""
        self.default_texture = default_texture
        self.textures = textures

        self.current_texture: pygame.Surface = self.default_texture

        self.seq = Sequence([])

        super().__init__(objet, self.default_texture,
                         self.default_texture.get_rect(), interface_nom)

    def set_current_texture(self, texture: pygame.Surface):
        """change la texture utilisée"""
        self.current_texture = texture

    def reset_anim(self):
        """reset les animations"""
        self.seq.fin()

    def start_anim(self, nom: str):
        """déclenche une animation"""
        self.seq = Sequence(
            [((self.set_current_texture, [tpl[0]]), tpl[1])
             for tpl in self.textures[nom]])
        self.seq.start()

    def check_next_anim(self) -> Tuple[pygame.Surface, bool]:
        """si le temps lié à l'animation est écoulé,
        passe à la texture suivante"""
        change = False
        if self.seq.seq_infos["is_running"]:
            change = self.seq.update()
        else:
            change = self.current_texture != self.default_texture
            self.current_texture = self.default_texture
        return self.current_texture, change

    def update(self):
        """méthode de mise à jour"""
        texture, change = self.check_next_anim()
        if change:
            self.elm_infos["surface"] = texture
            self.backup_rotation = 0
            self.elm_infos["rect"] = texture.get_rect()

        super().update()


class Bouton:
    """classe de représentation d'un bouton"""

    def __init__(self, pos: Vector3 | RelativePos,
                 surface: pygame.Surface, *, interface_nom: str,
                 data: Tuple[List[Any] | None,
                 Dict[str, Any] | None] = (None, None), **args: Any) -> None:
        self.pos = pos
        self.element = Element(
            self, surface, surface.get_rect(), interface_nom)

        fnct: Callable[..., Any] | None = args.get('fonction')
        if fnct is not None:
            self.fnct = fnct
        else:
            raise KeyError

        click = args.get('click')
        self.click = click if click is not None else 1

        self.nkdata = data[0] if data[0] is not None else []
        self.kdata = data[1] if data[1] is not None else {}


    def on_click(self, event: pygame.event.Event):
        """active lors du clique"""
        if self.click == event.button:
            self.fnct(*self.nkdata, **self.kdata)


class Texte:
    """gestion des textes"""

    def __init__(self, pos: Vector3 | RelativePos, interface_nom: str | None = None, **kwargs: Any) -> None:
        self.texte = kwargs.get('texte', '')
        self.pos = pos
        self.police, self.color = kwargs.get('police', POLICE), kwargs.get('couleur', '#FFFFFF')
        surface = self.police.render(self.texte, True, self.color)
        self.element = Element(
            self, surface, surface.get_rect(), interface_nom)

    def ajoute_lettre(self, lettre: str):
        """ajoute une lettre"""
        self.texte += lettre

    def update(self):
        """fonction de mise à jour"""
        self.element.elm_infos["surface"] = self.police.render(
            self.texte, True, self.color)
        self.element.elm_infos["rect"] = self.element.elm_infos["surface"].get_rect(
        )


class Draggable:
    """objet qu'on peut bouger"""

    dragged: 'None | Draggable' = None

    def __init__(self, pos: Vector3, surface: pygame.Surface, interface_nom: str) -> None:
        self.pos = pos
        self.state = 0
        self.element = Element(
            self, surface, surface.get_rect(), interface_nom)

    def on_click(self, event: pygame.event.Event):
        """gestion du clique"""
        if event.button == 1:
            Draggable.dragged = self
            self.state = 1
            self.pos.z += 1
            self.element.elm_infos['interface'].resort(self.element)

    def on_declick(self, event: pygame.event.Event):
        """gestion du relachement du clique"""
        self.state = 0
        self.pos.z -= 1
        self.element.elm_infos['interface'].resort(self.element)
        Draggable.dragged = None

    def update(self):
        """méthode de mise à jour"""
        if self.state:
            self.element.pos.x, self.element.pos.y = absolute_to_relpos(
                Vector3(*pygame.mouse.get_pos(), 0))
