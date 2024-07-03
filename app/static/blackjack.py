import random
import sqlite3

CARD_SUITS = ["H", "C", "D", "S"]
CARD_KEYS = ["2", "3", "4", "5", "6", "7", "8", "9", "10", "J", "Q", "K", "A"]
CARD_KEY_VALS = {"2": 2, "3": 3, "4": 4, "5": 5, "6": 6, "7": 7, "8": 8, "9": 9, "10": 10, "J": 10, "Q": 10, "K": 10, "A": [1, 11]}

DEFAULT_BET = 10
HAND_DELIM = "#"
CARD_DELIM = ","

# Player String Format: "hand1#hand2#...#handN"
# Hand   String Format: "card1,card2,...,cardN"

class Card:
    def __init__(self, key: str, suit: str) -> None:
        if key not in CARD_KEYS or suit not in CARD_SUITS:
            raise ValueError(f"Invalid card: {key}:{suit}")
        self.key = key
        self.suit = suit
        self.path = f"../static/svg_playing_cards/fronts/{suit}_{key}.svg"

    def __str__(self) -> str:
        return f"{self.suit}{self.key}"

class Deck:
    def __init__(self, num_decks: int, deck: str) -> None:
        self.num_decks = num_decks
        if deck != None:
            self.cards = []
            for card in deck.split(CARD_DELIM):
                try:
                    self.cards.append(Card(card[1:], card[0]))
                except ValueError as e:
                    print(f"Invalid card: {card} in deck string: {deck.split(CARD_DELIM)}")
        else:
            self.reset()
        
    def __str__(self) -> str:
        out = ""
        for card in self.cards:
            out += str(card)
            if card != self.cards[-1]:
                out += CARD_DELIM
        return out
    
    def __len__(self) -> int:
        return len(self.cards)

    def shuffle(self) -> None:
        shuffled = self.cards.copy()
        random.shuffle(shuffled)
        self.cards = shuffled

    def reset(self) -> None:
        self.cards = [Card(key, suit) for key in CARD_KEYS for suit in CARD_SUITS] * self.num_decks
        self.shuffle()

    def draw(self) -> Card:
        return self.cards.pop()

class Hand:
    def __init__(self, bet: int, hand: str) -> None:
        self.cards = []
        if hand != None:
            hand_list = hand.split(CARD_DELIM)
            for card in hand_list[1:]:
                # print("Card string: ", card)
                self.cards.append(Card(card[1:], card[0]))
        self.bet = bet
        self.score = 0
        self.score_ace = 0
        self.ace = False
        self.bust = False
        self.blackjack = False
        self.stand = False
        self.update_score()
        

    def __str__(self) -> str:
        out = str(self.bet) + ","
        for card in self.cards:
            out += str(card)
            if card != self.cards[-1]:
                out += ","        
        return out

    def deal(self, card: Card) -> None:
        self.cards.append(card)
        self.update_score()

    def update_score(self) -> None:
        self.score = 0
        self.score_ace = 0
        for card in self.cards:
            if card.key == "A":
                self.ace = True
                self.score += CARD_KEY_VALS[card.key][1]
                self.score_ace += CARD_KEY_VALS[card.key][0]
            else:
                self.score += CARD_KEY_VALS[card.key]
                self.score_ace += CARD_KEY_VALS[card.key]
        if self.score > 21 and self.ace:
            self.score = self.score_ace

        if self.score > 21:
            self.bust = True

        if self.score == 21:
            self.blackjack = True

    def pop(self) -> Card:
        popped = self.cards.pop()
        self.update_score()
        return popped


class Player:
    def __init__ (self, money: int, dealer_flag: bool, player : str) -> None:
        self.money = money
        self.hands = []
        self.num_hands = 0
        self.isDealer = dealer_flag
        if player != None:
            # print("Player string: ", player.split(HAND_DELIM))
            for hand in player.split(HAND_DELIM):
                # print("Hand string: ", hand)
                hand_list = hand.split(CARD_DELIM)
                bet = int(hand_list[0])
                self.hands.append(Hand(bet, hand))
                self.num_hands += 1
        else:
            self.add_hand(DEFAULT_BET)
    
    def __str__(self) -> str:
        out = ""
        for hand in self.hands:
            out += str(hand)
            if hand != self.hands[-1]:
                out += HAND_DELIM   
        return out

    def deal(self, card: Card, activeHand: int) -> None:
        self.hands[activeHand].deal(card)

    def add_hand(self, betAmt : int) -> None:
        if self.isDealer:
            bet = 0
        else:   
            bet = betAmt
        self.num_hands += 1
        self.hands.append(Hand(bet, None))

    def checkValidDouble(self) -> bool:
        return len(self.hands) == 1 and len(self.hands[0].cards) == 2 and self.money >= self.hands[0].bet * 2
        
    def checkValidSplit(self) -> bool:
        return len(self.hands) == 1 and len(self.hands[0].cards) == 2 and self.money >= self.hands[0].bet * 2
    
    def addMoney(self, amount: int) -> None:
        self.money += amount

    def subMoney(self, amount: int) -> None:
        self.money -= amount

    def reset(self) -> None:
        self.hands = []
        self.add_hand(DEFAULT_BET)

class Game:
    def __init__ (self, gs: sqlite3.Row) -> None:
        self.num_decks = 1
        
        if gs != None: # load game from gamestate
            self.player = Player(gs['money'], False, gs['player'])
            self.activeHandIndex = gs['activeHand']
            self.dealer = Player(0, True, gs['dealer'])
            self.deck = Deck(1, gs['deck'])
            self.over = bool(gs['over'])
            self.message = gs['message']
            self.disableBets = bool(gs['disableBets'])
        else: # new game
            self.player = Player(1000, False, None)
            self.activeHandIndex = 0
            self.dealer = Player(0, True, None)
            self.deck = Deck(self.num_decks, None)
            self.over = False
            self.message = ""
            self.disableBets = False
            self.initial_deal()
    

    def __str__ (self) -> str:
        out = "DEALER: "+ str(self.dealer)
        out += "\nPLAYER: "+ str(self.player)
        out += "\nHAND: " + str(self.activeHandIndex)
        out += "\nOVER: " + str(self.over)
        out += "\nMSG: " + self.message
        return out

    def reset(self) -> None:
        self.over = False
        self.disableBets = False
        self.message = ""
        self.activeHandIndex = 0
        if len(self.deck) < 10:
            self.deck.reset()
        self.deck.shuffle()
        self.dealer.reset()
        self.player.reset() 
        self.initial_deal()

    def initial_deal(self) -> None:
        for i in range(2):
            self.player.deal(self.deck.draw(), self.activeHandIndex)
        self.dealer.deal(self.deck.draw(), 0)
        self.logGameState()
    
    def hit(self, hand: Hand) -> None:
        hand.deal(self.deck.draw())

    def stand(self, hand: Hand) -> None:
        hand.stand = True

    def split(self, player: Player) -> None:
        player.hands.append(Hand(player.hands[0].bet, None))
        player.hands[1].deal(player.hands[0].pop())
        self.hit(player.hands[0])
        self.hit(player.hands[1])

    def double(self, player: Player) -> None:
        player.hands[0].bet *= 2
        self.hit(player.hands[0])
        player.hands[0].stand = True

    def validateAction(self, action: str) -> bool:
        result = False
        if action == "Bet":
            result = not self.disableBets
        elif action == "Play Again":
            result = self.over
        elif action == "Double":
            result = self.player.checkValidDouble() and self.disableBets and not self.over
        elif action == "Split":
            result = self.player.checkValidSplit() and not self.over and self.disableBets
        else:
            result = action in ["Hit", "Stand"] and not self.over and self.disableBets
        # print(f"Validating action: {action}...{result}")
        return result

    def resolveDisabled(self, b: bool) -> str:
        # print("Resolving disabled..." + str(b))
        if b == True: return "disabled"
        else: return ""

    def resolveCardPath(self, card: Card) -> str:
        if self.disableBets:
            return card.path
        else:
            return "../static/svg_playing_cards/backs/red.svg"

    def handlePlayerAction(self, action: str) -> None:
        # print("Handling player action..." + action)
        player = self.player
        hand = player.hands[self.activeHandIndex]
        if action == "Bet":
            self.disableBets = True
        if action == "Play Again":
            self.reset()
            return
        elif action == "Hit":
            self.hit(hand)
            # print("Player: ", player)
        elif action == "Stand":
            self.stand(hand)
        elif action == "Double":
            if player.checkValidDouble():
                self.double(player)
        elif action == "Split":
            if player.checkValidSplit():
                self.split(player) 

    def advanceGameState(self) -> None:
        # print("Advancing game state...")
        currHand = self.player.hands[self.activeHandIndex]
        # turn is over if player busts, gets blackjack, or stands
        if currHand.bust or currHand.blackjack or currHand.stand:
            # if last hand, move to dealer's turn   
            if self.activeHandIndex == len(self.player.hands) - 1:
                self.over = True
                self.logGameState()
                self.dealersTurn()
                self.checkWin()
                self.logGameState()
            else:
                self.activeHandIndex += 1

    def logGameState(self) -> None:
        connection = get_db_connection()
        # print("Logging gamestate...")
        # print(self)
        connection.execute('INSERT into gamestates (player, dealer, deck, activeHand, over, message, money, disableBets) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', (str(self.player), str(self.dealer), str(self.deck), self.activeHandIndex, self.over, self.message, self.player.money, self.disableBets))
        connection.commit()
        connection.close()

    def action(self, action: str) -> None:
        if not self.validateAction(action):
            return
            # raise ValueError("Invalid action: ", action)
        self.handlePlayerAction(action)
        self.advanceGameState()
        self.logGameState()
            

    def allPlayersBust(self) -> bool:
        for hand in self.player.hands:
            if not hand.bust:
                return False
        return True

    def checkWin(self) -> None:
        if self.dealer.hands[0].bust:
            for hand in self.player.hands:
                if not hand.bust:
                    self.message = "Player wins!"
                    self.player.addMoney(hand.bet)
                else: 
                    self.message = "Push!"
        else: # dealer not bust
            for hand in self.player.hands:
                if not hand.bust:
                    if hand.score > self.dealer.hands[0].score:
                        # # print("Player wins!")
                        self.message = "Player wins!"
                        self.player.addMoney(hand.bet)
                    elif hand.score < self.dealer.hands[0].score:
                        # # print("Dealer wins!")
                        self.message = "Dealer wins!"
                        self.player.subMoney(hand.bet)
                    else:
                        self.message = "Push!"
                        # # print("Push!")
                else:
                    self.player.subMoney(hand.bet)
                    self.message = "Dealer Wins!"

    def dealersTurn(self) -> None:
        self.hit(self.dealer.hands[0])
        if self.allPlayersBust():
            return
        while not self.dealer.hands[0].bust:
            max_score = 17
            for hand in self.player.hands:
                if hand.score > max_score:
                    max_score = hand.score
            if self.dealer.hands[0].score >= max_score:
                self.dealer.hands[0].stand = True
                break
            self.hit(self.dealer.hands[0])

def get_db_connection():
    # print("Getting db connection...")
    connection = sqlite3.connect('blackjack.db')
    tableExists = connection.execute('SELECT * FROM sqlite_master WHERE type="table" AND name="gamestates"').fetchall() != []
    if not tableExists:
        # print("Creating gamestates table...")
        with open('./BJschema.sql') as f:
            connection.executescript(f.read())
    connection.row_factory = sqlite3.Row
    return connection

def reset_db():
    # print("Resetting db...")
    connection = get_db_connection()
    connection.execute('DROP TABLE IF EXISTS gamestates')
    with open('./BJschema.sql') as f:
        connection.executescript(f.read())
    connection.commit()
    connection.close()

def get_current_gamestate():
    # print("Getting current gamestate...")
    connection = get_db_connection()
    bj_table = connection.execute('SELECT * FROM gamestates ORDER BY id DESC').fetchall()
    if len(bj_table) == 0: gamestate = None
    else: gamestate = bj_table[0]
    connection.commit()
    connection.close()
    # if gamestate != None:
        # print("Got gamestate: ", gamestate['id'])
    # else:
        # print("No gamestate found")
    return gamestate

