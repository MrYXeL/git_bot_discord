import os
import time
import asyncio
import discord
from discord.ext import commands
from dotenv import load_dotenv

from utils.embeds import casino_embed, blackjack_embed
from utils.game_logic import not_your

from slots import rd_slot_fruit, format_slots, mat, calcul_gain, rd
from manipDb import get_or_create_user, add_money, remove_money, get_daily, set_daily, top, get_user
from blackjack import draw_card, hand_value, has_blackjack

load_dotenv()

SLOT_PRICE = 3
DAILY_VALUE = 200

print(f"[{time.strftime("%Y-%m-%d %H:%M:%S")}] [INFO    ] Sarting Bot")

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)


@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"[{time.strftime("%Y-%m-%d %H:%M:%S")}] [INFO    ] Synchronized slash commands : {len(synced)}")
    except Exception as e:
        print(f"[{time.strftime("%Y-%m-%d %H:%M:%S")}] [ERROR   ] \n{e}")

    print(f"[{time.strftime("%Y-%m-%d %H:%M:%S")}] [INFO    ] Bot Ready To Use")


#----------------------------------------Class----------------------------------------
class SlotView(discord.ui.View):
    def __init__(self, author_id):
        super().__init__(timeout=30)
        self.author_id = author_id
        self.last_click = 0

    @discord.ui.button(label=f"Play Again 🎰 ${SLOT_PRICE}", style=discord.ButtonStyle.green, row=0)
    async def replay(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await not_your(interaction, self.author_id):
            return

        #coldown
        '''
        button.disabled = True
        await interaction.response.edit_message(view=self)
        await asyncio.sleep(1)
        button.disabled = False
        await interaction.edit_original_response(view=self)
        '''

        current_money = get_or_create_user(self.author_id)
        if (current_money-SLOT_PRICE) >= 0:
            current_money -= SLOT_PRICE
            remove_money(self.author_id, SLOT_PRICE)
            win = rd()
            result = format_slots(win)
            gain = calcul_gain(win)

            embed = discord.Embed(
                title="🎰 Slot Machine",
                description=result
            )
            if gain != 0:
                current_money += gain
                add_money(self.author_id, gain)

            embed.add_field(name="", value=f"Current Balance : **{current_money}**")   

            await interaction.response.edit_message(embed=embed)
        else:
            await interaction.response.send_message(
                    "❌ You don't have enough money !\nWait for the next /daily",
                    ephemeral=True
                )
    
    @discord.ui.button(label=f"Slot Info 📋", style=discord.ButtonStyle.gray, row=1)
    async def listslot(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = discord.Embed(title="Fruits Values")

        for fruit in mat:
            embed.add_field(
                name="",
                value=f"**{fruit[2]}%** {fruit[0]} **:** **{fruit[1]}**",
                inline=False
            )

        await interaction.response.send_message(embed=embed, ephemeral=True)

    @discord.ui.button(label=f"Casino Menu 🎲", style=discord.ButtonStyle.gray, row=2)
    async def menu(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed = casino_embed(interaction.user)

        await interaction.response.edit_message(
                embed=embed,
                view=PlayView(interaction.user.id)
            )

class Back(discord.ui.View):
    def __init__(self, author_id):
        super().__init__(timeout=30)
        self.author_id = author_id

    @discord.ui.button(label="Back", style=discord.ButtonStyle.gray, row=4)
    async def play(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        can_daily = can_claim_daily(user_id)
        if can_daily:
            add_money(user_id, DAILY_VALUE)
            set_daily(user_id)
        embed = casino_embed(interaction.user)
        if can_daily:
            embed.add_field(name="💰 Daily", value=f"You have claim your daily credits and got ${DAILY_VALUE}")


        await interaction.response.send_message(
                embed=embed,
                view=PlayView(interaction.user.id)
            )

class replayblackjack(discord.ui.View):
    def __init__(self, author_id):
        super().__init__(timeout=30)
        self.author_id = author_id

    @discord.ui.button(label="Replay", style=discord.ButtonStyle.red, row=4)
    async def replay(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await not_your(interaction, self.author_id):
            return

        await interaction.response.send_modal(
            BetModal(self.author_id)
        )
    
    @discord.ui.button(label="Casino Menu 🎲", style=discord.ButtonStyle.gray, row=4)
    async def play(self, interaction: discord.Interaction, button: discord.ui.Button):
        user_id = interaction.user.id
        embed = casino_embed(interaction.user)

        if can_claim_daily(user_id):
            add_money(user_id, DAILY_VALUE)
            set_daily(user_id)
            embed.add_field(name="💰 Daily", value=f"You have claim your daily credits and got ${DAILY_VALUE}")


        await interaction.response.send_message(
                embed=embed,
                view=PlayView(interaction.user.id)
            )

class BlackjackView(discord.ui.View):
    def __init__(self, author_id, bet, player, bank, drawed_list):
        super().__init__(timeout=60)
        self.author_id = author_id
        self.bet = bet
        self.player = player
        self.bank = bank
        self.drawed_list = drawed_list

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.green, row=0)
    async def hit(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await not_your(interaction, self.author_id):
            return
        
        embed = blackjack_embed(interaction, self.bet)
        drawed = draw_card(self.drawed_list)
        self.player.append(drawed)
        self.drawed_list.append(drawed)
        p_v = hand_value(self.player)
        b_v = hand_value([self.bank[0]])

        embed.add_field(
            name="Bank's Hand",
            value=(" **|** ".join(f"{n} {c}" for n, c in [self.bank[0]])) + f" **|** ?? Total: {b_v}+??",
            inline=False
        )
        embed.add_field(
            name=f"{interaction.user.display_name}'s Hand",
            value=(" **|** ".join(f"{n} {c}" for n, c in self.player)) + f" Total: {p_v}",
            inline=False
        )

        if p_v>21:
            b_v = hand_value(self.bank)
            embed.set_field_at(
                0,
                name="Bank's Hand",
                value=(" **|** ".join(f"{n} {c}" for n, c in self.bank)) + f" Total: {b_v}",
                inline=False
            )
            embed.set_field_at(
                1,
                name=f"{interaction.user.display_name}'s Hand",
                value=(" **|** ".join(f"{n} {c}" for n, c in self.player)) + f" Total: {p_v}",
                inline=False
            )
            embed.add_field(name="Result", value=f"You have more than 21\nYou lost")
            await interaction.response.edit_message(embed=embed,view=replayblackjack(self.author_id))
        else:
            await interaction.response.edit_message(embed=embed,view=self)


    @discord.ui.button(label="Stand", style=discord.ButtonStyle.green, row=0)
    async def stand(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await not_your(interaction, self.author_id):
            return
        
        embed = blackjack_embed(interaction, self.bet)
        p_v = hand_value(self.player)
        b_v = hand_value(self.bank)

        if has_blackjack(self.bank):
            embed.add_field(
                name="Bank's Hand",
                value=(" **|** ".join(f"{n} {c}" for n, c in self.bank)) + f" Total: {b_v}",
                inline=False
            )
            embed.add_field(
                name=f"{interaction.user.display_name}'s Hand",
                value=(" **|** ".join(f"{n} {c}" for n, c in self.player)) + f" Total: {p_v}",
                inline=False
            )
            embed.add_field(name="", value=f"The Bank has blackjack\nYou lost")
            await interaction.response.edit_message(embed=embed, view=replayblackjack(self.author_id))
        else:
            embed.add_field(
                name="Bank's Hand",
                value=(" **|** ".join(f"{n} {c}" for n, c in self.bank)) + f" Total: {b_v}",
                inline=False
            )
            embed.add_field(
                name=f"{interaction.user.display_name}'s Hand",
                value=(" **|** ".join(f"{n} {c}" for n, c in self.player)) + f" Total: {p_v}",
                inline=False
            )

            await asyncio.sleep(1)
            await interaction.response.edit_message(embed=embed)
            message = await interaction.original_response()
            
            while(b_v < 17):
                drawed = draw_card(self.drawed_list)
                self.bank.append(drawed)
                self.drawed_list.append(drawed)
                b_v = hand_value(self.bank)
                embed.set_field_at(
                    0,
                    name="Bank's Hand",
                    value=(" **|** ".join(f"{n} {c}" for n, c in self.bank)) + f" Total: {b_v}\nBank drawed a card",
                    inline=False
                )
                embed.set_field_at(
                    1,
                    name=f"{interaction.user.display_name}'s Hand",
                    value=(" **|** ".join(f"{n} {c}" for n, c in self.player)) + f" Total: {p_v}",
                    inline=False
                )
                await asyncio.sleep(1)
                await message.edit(embed=embed)

            if b_v > 21:
                embed.set_field_at(
                    0,
                    name="Bank's Hand",
                    value=(" **|** ".join(f"{n} {c}" for n, c in self.bank)) + f" Total: {b_v}",
                    inline=False
                )
                embed.set_field_at(
                    1,
                    name=f"{interaction.user.display_name}'s Hand",
                    value=(" **|** ".join(f"{n} {c}" for n, c in self.player)) + f" Total: {p_v}",
                    inline=False
                )
                embed.add_field(name="", value=f"The Bank has Bust\nYou won ${(self.bet)*2}")
                add_money(self.author_id, (self.bet)*2)
            else:
                if p_v > b_v:
                    embed.set_field_at(
                        0,
                        name="Bank's Hand",
                        value=(" **|** ".join(f"{n} {c}" for n, c in self.bank)) + f" Total: {b_v}",
                        inline=False
                    )
                    embed.set_field_at(
                    1,
                        name=f"{interaction.user.display_name}'s Hand",
                        value=(" **|** ".join(f"{n} {c}" for n, c in self.player)) + f" Total: {p_v}",
                        inline=False
                    )
                    embed.add_field(name="Result", value=f"You have more than the Bank\nYou won ${(self.bet)*2}")
                    add_money(self.author_id, (self.bet)*2)
                elif b_v > p_v:
                    embed.set_field_at(
                        0,
                        name="Bank's Hand",
                        value=(" **|** ".join(f"{n} {c}" for n, c in self.bank)) + f" Total: {b_v}",
                        inline=False
                    )
                    embed.set_field_at(
                        1,
                        name=f"{interaction.user.display_name}'s Hand",
                        value=(" **|** ".join(f"{n} {c}" for n, c in self.player)) + f" Total: {p_v}",
                        inline=False
                    )
                    embed.add_field(name="Result", value=f"You lost, the Bank has more than you")
                else:
                    embed.set_field_at(
                        0,
                        name="Bank's Hand",
                        value=(" **|** ".join(f"{n} {c}" for n, c in self.bank)) + f" Total: {b_v}",
                        inline=False
                    )
                    embed.set_field_at(
                        1,
                        name=f"{interaction.user.display_name}'s Hand",
                        value=(" **|** ".join(f"{n} {c}" for n, c in self.player)) + f" Total: {p_v}",
                        inline=False
                    )
                    embed.add_field(name="Result", value=f"You have as much as the Bank\nYou got back ${(self.bet)}")
                    add_money(self.author_id, (self.bet))
            await asyncio.sleep(1)
            await message.edit(embed=embed, view=replayblackjack(self.author_id))


    @discord.ui.button(label="Double", style=discord.ButtonStyle.green, row=0)
    async def double(self, interaction: discord.Interaction, button: discord.ui.Button):
        if await not_your(interaction, self.author_id):
            return
        
        remove_money(self.author_id, self.bet)
        embed = blackjack_embed(interaction, (self.bet)*2)
        self.bet = (self.bet)*2
        drawed = draw_card(self.drawed_list)
        self.player.append(drawed)
        self.drawed_list.append(drawed)
        p_v = hand_value(self.player)
        b_v = hand_value([self.bank[0]])

        embed.add_field(
            name="Bank's Hand",
            value=(" **|** ".join(f"{n} {c}" for n, c in [self.bank[0]])) + f" **|** ?? Total: {b_v}+??",
            inline=False
        )
        embed.add_field(
            name=f"{interaction.user.display_name}'s Hand",
            value=(" **|** ".join(f"{n} {c}" for n, c in self.player)) + f" Total: {p_v}",
            inline=False
        )

        if p_v>21:
            b_v = hand_value([self.bank[0]])
            embed.set_field_at(
                0,
                name="Bank's Hand",
                value=(" **|** ".join(f"{n} {c}" for n, c in self.bank)) + f" Total: {b_v}",
                inline=False
            )
            embed.set_field_at(
                1,
                name=f"{interaction.user.display_name}'s Hand",
                value=(" **|** ".join(f"{n} {c}" for n, c in self.player)) + f" Total: {p_v}",
                inline=False
            )
            embed.add_field(name="Result", value=f"You have more than 21\nYou lost")
            await interaction.response.edit_message(embed=embed,view=replayblackjack(self.author_id))
        else:
            await interaction.response.edit_message(embed=embed,view=self)

class BetModal(discord.ui.Modal, title="♠️ BlackJack - Place your bet"):
    bet = discord.ui.TextInput(
        label="Your bet",
        placeholder="Enter an amount",
        required=True,
        max_length=10
    )

    def __init__(self, author_id):
        super().__init__()
        self.author_id = author_id

    async def on_submit(self, interaction: discord.Interaction):
        if await not_your(interaction, self.author_id):
            return

        if not self.bet.value.isdigit():
            await interaction.response.send_message(
                "❌ Please enter a valid number",
                ephemeral=True
            )
            return

        bet_amount = int(self.bet.value)

        balance = get_or_create_user(interaction.user.id)
        if bet_amount <= 0 or bet_amount > balance:
            await interaction.response.send_message(
                "❌ Invalid bet amount",
                ephemeral=True
            )
            return

        remove_money(self.author_id, bet_amount)

        embed = blackjack_embed(interaction, self.bet)

        drawed_list = []
        player = []
        bank = []

        # Player 1
        drawed = draw_card(drawed_list)
        player.append(drawed)
        drawed_list.append(drawed)

        # Bank 1
        drawed = draw_card(drawed_list)
        bank.append(drawed)
        drawed_list.append(drawed)

        # Player 2
        drawed = draw_card(drawed_list)
        player.append(drawed)
        drawed_list.append(drawed)

        # Bank 2
        drawed = draw_card(drawed_list)
        bank.append(drawed)
        drawed_list.append(drawed)

        p_v = hand_value(player)
        b_v = hand_value(bank)

        embed.add_field(
            name="Bank's Hand",
            value=(" **|** ".join(f"{n} {c}" for n, c in [bank[0]])) + f" **|** ?? Total: {hand_value([bank[0]])}+??",
            inline=False
        )
        embed.add_field(
            name=f"{interaction.user.display_name}'s Hand",
            value=(" **|** ".join(f"{n} {c}" for n, c in player)) + f" Total: {p_v}",
            inline=False
        )


        if has_blackjack(player):
            if has_blackjack(bank):
                embed.set_field_at(
                    0,
                    name="Bank's Hand",
                    value=(" **|** ".join(f"{n} {c}" for n, c in bank)) + f" Total: {b_v}",
                    inline=False
                )
                embed.set_field_at(
                    1,
                    name=f"{interaction.user.display_name}'s Hand",
                    value=(" **|** ".join(f"{n} {c}" for n, c in player)) + f" Total: {p_v}",
                    inline=False
                )
                embed.add_field(name="Result", value=f"You and the bank has a blackjack\nYou got back ${(bet_amount)}")
            else:
                embed.set_field_at(
                    0,
                    name="Bank's Hand",
                    value=(" **|** ".join(f"{n} {c}" for n, c in bank)) + f" Total: {b_v}",
                    inline=False
                )
                embed.set_field_at(
                1,
                    name=f"{interaction.user.display_name}'s Hand",
                    value=(" **|** ".join(f"{n} {c}" for n, c in player)) + f" Total: {p_v}",
                    inline=False
                )
                embed.add_field(name="Result", value=f"You have a blackjack\nYou won ${(bet_amount)+ bet_amount*1.5}")
            await interaction.response.edit_message(embed=embed,view=replayblackjack(self.author_id))

        await interaction.response.edit_message(
            embed=embed,
            view=BlackjackView(
                self.author_id,
                bet_amount,
                player,
                bank,
                drawed_list
            )
        )
     
class PlayView(discord.ui.View):
    def __init__(self, author_id):
        super().__init__(timeout=30)
        self.author_id = author_id

    @discord.ui.button(label=f"LeaderBoard 📋", style=discord.ButtonStyle.gray, row=0)
    async def leaderboard(self, interaction: discord.Interaction, button: discord.ui.Button):
        embed=discord.Embed(title="📋 LeaderBoard")
        top10 = top(1,10)
        rank = 1
        for user_id, money in top10:
            try:
                user = await bot.fetch_user(user_id)
                name = user.display_name
            except:
                name = f"User {user_id}"
            embed.add_field(name="", value=f"#{rank} {name} ${money}", inline=False)

            rank +=1
        await interaction.response.edit_message(embed=embed,view=Back(self.author_id))

    @discord.ui.button(label=f"Play Slot Machine 🎰 ${SLOT_PRICE}", style=discord.ButtonStyle.green, row=1)
    async def slotmachine(self, interaction: discord.Interaction, button: discord.ui.Button):

        if await not_your(interaction, self.author_id):
            return

        user_id = interaction.user.id
        current_money = get_or_create_user(user_id)
        if (current_money-SLOT_PRICE) >= 0:
            current_money -= SLOT_PRICE
            remove_money(user_id, SLOT_PRICE)
            win = rd()
            result = format_slots(win)
            gain = calcul_gain(win)

            embed = discord.Embed(
                title="🎰 Slot Machine",
                description=result
            )
            if gain != 0:
                current_money += gain
                add_money(user_id, gain)

            embed.add_field(name="", value=f"Current Balance : **{current_money}**")   

            await interaction.response.edit_message(
                embed=embed,
                view=SlotView(interaction.user.id)
            )
        else:
            await interaction.response.send_message(
                    "❌ You don't have enough money !\nWait for the next /daily",
                    ephemeral=True
                )
            
    @discord.ui.button(label="♠️ Blackjack", style=discord.ButtonStyle.green, row=2)
    async def blackjack(self, interaction: discord.Interaction, button: discord.ui.Button):
        if interaction.user.id != self.author_id:
            if await not_your(interaction, self.author_id):
                return

        await interaction.response.send_modal(
            BetModal(self.author_id)
        )
            
#-------------------------------------------Utilities-------------------------------------------
def can_claim_daily(user_id):
    last_daily = get_daily(user_id)
    if last_daily is None:
        return True

    return time.time() - last_daily >= 86400

#----------------------------------------Profile-----------------------------------------
@bot.tree.command(name="profile", description="Show the profile of a player")
async def profile(interaction: discord.Interaction, player: discord.User):
    if get_user(player.id) == -1:
        info = "This player haven't played yet"
    else:
        info = f"{player.display_name} has ${get_user(player.id)}"
    embed=discord.Embed(
        title=f"📋 {player.display_name}'s Profile",
        description=info
    )
    embed.set_thumbnail(url=player.avatar.url)
    await interaction.response.send_message(embed=embed)
    
#------------------------------------------Main Menu------------------------------------------
@bot.tree.command(name="play", description="Start to play")
async def play(interaction: discord.Interaction):
    user_id = interaction.user.id
    embed = casino_embed(interaction.user)
    if can_claim_daily(user_id):
        add_money(user_id, DAILY_VALUE)
        set_daily(user_id)

        embed.add_field(
            name="💰 Daily", 
            value=f"You have claim your daily credits and got ${DAILY_VALUE}")


    await interaction.response.send_message(
            embed=embed,
            view=PlayView(interaction.user.id)
        )



#TODO voir /daily attendre 24h exactement ou quand changement de jour ?

#TODO verifier anglais
#TODO embed Refactor factory, utils



bot.run(os.getenv("TOKEN"))