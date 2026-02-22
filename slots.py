from random import randint

# Données des fruits
#icone, valeur, nb par rouleau
mat = [
    [":cherries:", 1, 5],       #25 %
    [":lemon:", 2, 4],          #20 %
    [":tangerine:", 3, 3],      #15 %
    [":bell:", 5, 3],           #15 %
    [":star:", 8, 2],           #10 %
    [":gem:", 15, 2],           #10 %
    [":crown:",30, 1]           #5  %
]

def rd_slots(dispo):
    i = randint(0, len(dispo) - 1)
    return dispo.pop(i)

def rd():
    slots = [
        [-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1],
        [-1,-1,-1,-1,-1]
    ]

    for i in range(5):
        dispo = [0,0,0,0,0,1,1,1,1,2,2,2,3,3,3,4,4,5,5,6]

        for j in range(3):
            slots[j][i] = rd_slots(dispo)

    return slots

def slots_affiche(slots):
    string = ""
    for i in range(3):
        for j in range(5):
            string = string + f" **|** {mat[slots[i][j]][0]}"
        if i < 2:
            string = string + " **|**\n"
        else:
            string = string + " **|**"
    return string


def calcul_gain(slots):
    #ligne
    #colone
    
    
    
    #diag après
    pass