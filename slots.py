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
    gain = 0
    #ligne de 3 x1
    #ligne de 4 x2
    #ligne de 5 x3
    #colone x1
    #diag \ x1 
    #diag / x1

    #colone
    for col in range(5):
        if (slots[0][col] != slots[1][col]):
            pass
        elif (slots[1][col] == slots[2][col]):
            gain += mat[slots[0][col]][1]
            print("col")
    #diag \
    for i in range(3):
        if (slots[0][i] == slots[1][i+1] == slots[2][i+2]):
            gain += mat[slots[0][i]][1]
            print("diag hg to bd")
    #diag /
    for i in range(2 , 5):
        if (slots[0][i] == slots[1][i-1] == slots[2][i-2]):
            gain += mat[slots[0][i]][1]
            print("diag hd to bg")
    #ligne 5
    li_done = []
    for li in range(3):
        if (slots[li][0] == slots[li][1] == slots[li][2] == slots[li][3] == slots[li][4]):
            gain += (3 * mat[slots[li][2]][1])
            li_done.append(li)
            print("l5")
    #ligne 4
    for li in range(3):
        if not (li in li_done):
            if (slots[li][0] == slots[li][1] == slots[li][2] == slots[li][3] or slots[li][1] == slots[li][2] == slots[li][3] == slots[li][4]):
                gain += (2 * mat[slots[li][2]][1])
                li_done.append(li)
                print("l4")
    #ligne 3
    for li in range(3):
        if not (li in li_done):
            if (slots[li][0] == slots[li][1] == slots[li][2] or slots[li][1] == slots[li][2] == slots[li][3] or slots[li][2] == slots[li][3] == slots[li][4]):
                gain += (mat[slots[li][2]][1])
                li_done.append(li)
                print("l3")

    return gain