from random import randint

# Données des fruits
mat = [
    [":banana:", 1, 35],
    [":lemon:", 3, 25],
    [":cherries:", 5, 18],
    [":apple:", 10, 12],
    [":pear:", 15, 7],
    [":grapes:", 20, 3]
]

def rd():
    r = randint(1,100)
    if r <= 10:
        r = randint(1, 100)
        if 1 <= r <= 35:
            fruit = 0
        elif 36 <= r <= 60:
            fruit = 1
        elif 61 <= r <= 78:
            fruit = 2
        elif 79 <= r <= 90:
            fruit = 3
        elif 91 <= r <= 97:
            fruit = 4
        else:
            fruit = 5
        return fruit
    return -1

def rd_slot_fruit() -> list[int]:
    slots = [-1, -1, -1]
    while(slots[0] == slots[1] and slots[1] == slots[2]):
        for i in range(3):
            r = randint(1, 100)
            if 1 <= r <= 35:
                fruit = 0
            elif 36 <= r <= 60:
                fruit = 1
            elif 61 <= r <= 78:
                fruit = 2
            elif 79 <= r <= 90:
                fruit = 3
            elif 91 <= r <= 97:
                fruit = 4
            else:
                fruit = 5
            slots[i] = fruit
    return slots


def format_slots(fruit: int):
    if fruit != -1:
        return (
            f"\n{mat[fruit][0]} **|** {mat[fruit][0]} **|** {mat[fruit][0]}\n"
            f"\nYou won ${calcul_gain(fruit)} !"
        )
    else:
        slots = rd_slot_fruit()
        return (
            f"\n{mat[slots[0]][0]} **|** {mat[slots[1]][0]} **|** {mat[slots[2]][0]}\n"
            f"\nYou lost !"
        )
    
def calcul_gain(fruit: int):
    if fruit != -1:
        return mat[fruit][1] * 3
    return 0