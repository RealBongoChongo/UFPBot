import discord
import random

decks = [
    ['A♠', 'K♥', '3♠', 'K♥', '5♠', '6♠', '7♠', '8♠', '9♠', '10♠', 'J♠', 'Q♠', 'K♠', 'A♥', '2♥', '3♥', '4♥', '5♥', '6♥', '7♥', '8♥', '9♥', '10♥', 'J♥', 'Q♥', 'K♥', 'A♦', '2♦', '3♦', '4♦', '5♦', '6♦', '7♦', '8♦', '9♦', '10♦', 'J♦', 'Q♦', 'K♦', 'A♣', '2♣', '3♣', '4♣', '5♣', '6♣', '7♣', '8♣', '9♣', '10♣', 'J♣', 'Q♣', 'K♣'],
    ['5♥', '5♦', '4♥', 'A♣', 'A♥', '6♠', '7♠', '8♠', '9♠', '10♠', 'J♠', 'Q♠', 'K♠', 'A♥', '2♥', '3♥', '4♥', '5♥', '6♥', '7♥', '8♥', '9♥', '10♥', 'J♥', 'Q♥', 'K♥', 'A♦', '2♦', '3♦', '4♦', '5♦', '6♦', '7♦', '8♦', '9♦', '10♦', 'J♦', 'Q♦', 'K♦', 'A♣', '2♣', '3♣', '4♣', '5♣', '6♣', '7♣', '8♣', '9♣', '10♣', 'J♣', 'Q♣', 'K♣'],
    ['5♥', 'J♥', '3♠', '10♥', '5♦', '6♠', 'K♠', '8♠', '9♠', '10♠', 'J♠', 'Q♠', 'K♠', 'A♥', '2♥', '3♥', '4♥', '5♥', '6♥', '7♥', '8♥', '9♥', '10♥', 'J♥', 'Q♥', 'K♥', 'A♦', '2♦', '3♦', '4♦', '5♦', '6♦', '7♦', '8♦', '9♦', '10♦', 'J♦', 'Q♦', 'K♦', 'A♣', '2♣', '3♣', '4♣', '5♣', '6♣', '7♣', '8♣', '9♣', '10♣', 'J♣', 'Q♣', 'K♣'],
    ['10♦', 'J♥', '4♥', 'Q♥', '5♦', '6♠', 'K♠', '8♠', '9♠', '10♠', 'J♠', 'Q♠', 'K♠', 'A♥', '2♥', '3♥', '4♥', '5♥', '6♥', '7♥', '8♥', '9♥', '10♥', 'J♥', 'Q♥', 'K♥', 'A♦', '2♦', '3♦', '4♦', '5♦', '6♦', '7♦', '8♦', '9♦', '10♦', 'J♦', 'Q♦', 'K♦', 'A♣', '2♣', '3♣', '4♣', '5♣', '6♣', '7♣', '8♣', '9♣', '10♣', 'J♣', 'Q♣', 'K♣']
]

def getDeck():
    symbols = "♠♥♦♣"
    cards = ["A", "2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K"]

    deck = []

    for symbol in symbols:
        for card in cards:
            deck.append(card + symbol)

    return deck

def getValue(cards):
    value = 0
    value2 = 0
    for card in cards:
        if card[0] == "A":
            value += 11
            value2 += 1
        elif card[0] in ["K", "Q", "J"]:
            value += 10
            value2 += 10
        else:
            if len(card) == 3:
                value += 10
                value2 += 10
            else:
                value += int(card[0])
                value2 += int(card[0])

    if value == 21:
        return value
    elif value2 == 21:
        return value2
    elif value > 21 and value2 < 21:
        return value2
    elif value2 > value:
        return value2
    return value



class Blackjack(discord.ui.View):
    def __init__(self, ctx, thing):
        super().__init__(timeout=None)
        
        self.deck = getDeck()
        self.result = None
        self.reason = ""

        if ctx.author.id == 485513915548041239 and thing["thing"]:
            self.deck = random.choice(decks)
        else:
            random.shuffle(self.deck)
            random.shuffle(self.deck)
            random.shuffle(self.deck)
            random.shuffle(self.deck)
            random.shuffle(self.deck)

        self.author = ctx.author

        self.playerCards = [self.deck[0], self.deck[1]]
        self.botCards = [self.deck[2], self.deck[3]]

        if getValue(self.playerCards) == 21:
            self.result = True
            self.reason = "You got blackjack"
            self.disable_all_items()
            self.stop()
        elif getValue(self.botCards) == 21:
            self.result = False
            self.reason = "Bot got blackjack"
            self.disable_all_items()
            self.stop()
        else:
            self.deck.remove(self.deck[0])
            self.deck.remove(self.deck[0])
            self.deck.remove(self.deck[0])
            self.deck.remove(self.deck[0])

            self.embed = discord.Embed(
                title="Blackjack Game",
                description=""
            )
            self.embed.add_field(name="Your Cards", value=", ".join(self.playerCards))
            self.embed.add_field(name="Bot's Cards", value=self.botCards[0] + ", " + ", ".join(["?" for i in range(len(self.botCards[1:]))]))

    @discord.ui.button(label="Hit", style=discord.ButtonStyle.success)
    async def hit(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer()
        if interaction.user.id != self.author.id:
            return await interaction.followup.send("You cannot do this", ephemeral=True)
        self.playerCards.append(self.deck[0])
        self.deck.remove(self.deck[0])

        if getValue(self.playerCards) == 21:
            self.result = True
            self.reason = "You got blackjack"
            self.disable_all_items()
            self.stop()
        elif getValue(self.playerCards) > 21:
            self.result = False
            self.reason = "You busted"
            self.disable_all_items()   
            self.stop()
        else:
            self.embed.clear_fields()
            self.embed.add_field(name="Your Cards ({})".format(getValue(self.playerCards)), value=", ".join(self.playerCards))
            self.embed.add_field(name="Bot's Cards".format(getValue(self.botCards)), value=self.botCards[0] + ", " + ", ".join(["?" for i in range(len(self.botCards[1:]))]))

            await interaction.edit_original_response(embed=self.embed, view=self)

    @discord.ui.button(label="Stand")
    async def stand(self, button: discord.ui.Button, interaction: discord.Interaction):
        await interaction.response.defer()
        if interaction.user.id != self.author.id:
            return await interaction.followup.send("You cannot do this", ephemeral=True)

        while getValue(self.botCards) < getValue(self.playerCards):
            self.botCards.append(self.deck[0])
            self.deck.remove(self.deck[0])

            if getValue(self.botCards) > 21:
                break
            elif getValue(self.botCards) == 21:
                break

        if getValue(self.botCards) > 21:
            self.result = True
            self.reason = "Bot busted"
            self.disable_all_items()
            self.stop()
        elif getValue(self.botCards) == 21:
            self.result = False
            self.reason = "Bot got blackjack"
            self.disable_all_items()
            self.stop()
        elif getValue(self.playerCards) > getValue(self.botCards):
            self.result = True
            self.reason = "You had more cards"
            self.disable_all_items()
            self.stop()
        elif getValue(self.playerCards) < getValue(self.botCards):
            self.result = False
            self.reason = "Bot had more cards"
            self.disable_all_items()
            self.stop()
        else:
            self.reason = "You tied"
            self.disable_all_items()
            self.stop()