import discord
from manipDb import get_or_create_user

def casino_embed(user):
    bal = get_or_create_user(user.id)
    return discord.Embed(
        title=f"🎲 {user.display_name}'s Casino",
        description=f"You currently have ${bal}"
    )

def blackjack_embed(id, name, bet):
    return discord.Embed(title=f"♠️ {name}'s BlackJack", description=f"Your bet : ${bet}\nYou have ${(get_or_create_user(id))}")