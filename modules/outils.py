"""module outils"""
from typing import List


# fonctions

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
        elif liste[mid] > valeur:
            end = mid
        else:
            start = mid + 1
    
    return start + 1 if valeur > liste[start] else start
