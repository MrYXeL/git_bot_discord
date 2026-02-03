from random import randint

COLOR = [":diamonds:", ":hearts:", ":spades:", ":clubs:" ]
NUMBER = ["A","2","3","4","5","6","7","8","9","J","Q","K"]

def draw_card(t):
    '''t : cards already drawed'''
    drawed_color = COLOR[randint(0,3)]
    drawed_number = NUMBER[randint(0,11)]
    drawed = (drawed_number, drawed_color)
    while(drawed in t):
        drawed_color = COLOR[randint(0,3)]
        drawed_number = NUMBER[randint(0,11)]
        drawed = (drawed_number, drawed_color)
    return(drawed)

def hand_value(hand):
    v = 0
    nb_as = 0
    for number, _ in hand:
        if number.isdigit() or number == "A":
            if number == "A":
                nb_as += 1
                v += 1
            else:
                v += int(number)
        else:  # J Q K
            v += 10

    # verif si as passe a 11 ou non 
    for _ in range(nb_as):
        if v + 10 <= 21:
            v += 10

    return v

def has_blackjack(hand):
    if (hand[0][0] == "1" and hand[1][0] in ["J", "Q", "K"]) or (hand[1][0] == "1" and hand[0][0] in ["J", "Q", "K"]):
        return True
    return False