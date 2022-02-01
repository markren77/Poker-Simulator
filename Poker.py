import socket
import random

#An object of player
class player:
    
    #Constructor
    def __init__(self, z):
        #card1 and card2 are objects of the class card
        self.card1=None
        self.card2=None
        #client is for sending information back and forth between client and server
        self.client = z
        #chips
        self.money = 10000
        #False means they haven't done the following in the betting process
        self.fold=False
        self.check=False
        #how much they have bet so far in each hand
        self.currentBet=0

    #uses the card class methods to return a printable version of the player's cards
    def getCards(self):
        return self.card1.getCard()+", "+self.card2.getCard()

class card:
    #constructor
    def __init__(self, x, y):
        #face is what kind of card, value is the number on it
        #the values will be from 2 to 14, with 14 being Ace
        self.face = x
        self.value = y
    def getCard(self):
        return str(self.face)+" "+switch_value(self.value)

#a method used for displaying the current community cards
def displayCards():
    if len(communityCard)==0:
        return "Community Cards:\nCurrently in blinds\n"
    toReturn="Community Cards:\n"
    for x in communityCard:
        toReturn+= f"{x.getCard()}\n"
    return toReturn

#Switch Case statement used for creating cards
def switch_hand(x):
    switcher={
        0:"♥",
        1:"♠",
        2:"♣",
        3:"♦"
    }
    return switcher.get(x, "Invalid arguement")

#Switch case statement used for printing the 11 12 13 14 on the cards
def switch_value(x):
    switcher={
        11:"Jack",
        12:"Queen",
        13:"King",
        14:"Ace"
    }
    return switcher.get(x, str(x))

#checks if all other players have folded
def foldCheck(j):
    for x in range(len(playerList)):
        if x==j:
            continue
        if playerList[x].fold==False:
            return False
    return True

#checks if a player has won
#whether if that player is the only one left with money
def winCon():
    winCheck = len(playerList)
    for x in playerList:
        if x.money<=0:
            winCheck-=1
    return winCheck==1

#returns who is the winner
#0 if there isn't a winner yet
def winnerCheck():
    for x in range(len(playerList)):
        if playerList[x].money>0:
            return x+1
    return 0

#checks if a card already exists on the community cards or player hands
#all cards will go in this variable called allCards beforehand to make this process easier
def duplicateCheck(card):
    global allCards
    for c in allCards:
        if card.getCard().strip()==c.getCard().strip():
            return True
    return False

#AKA betting process
def turn(start):
    global playerList
    global pot
    global highestBet
    global winner
    betting = True
    turnEdit=True
    for p in playerList:
        p.check=False
    while betting:
        for i in range(len(playerList)):
            if turnEdit:
                i=start
                turnEdit=False
            if foldCheck(i):
                winner = i+1
                break
            if playerList[i].money==0:
                playerList[i].check=True
            
            if playerList[i].money!=0 and playerList[i].fold==False and playerList[i].currentBet<highestBet:
                for x in range(len(playerList)):
                    playerList[x].client.send("-----------------------------------------------------------\n".encode())
                    playerList[x].client.send(f"~~Player {i+1}'s Turn~~\n".encode())
                playerList[i].client.send(displayCards().encode())
                playerList[i].client.send(f"Your cards:\n{playerList[i].getCards()}\n".encode())
                playerList[i].client.send(f"\nPot chips are {pot}\n".encode() )
                for x in range(len(playerList)):
                    if x!=i:
                        if playerList[x].fold==True:
                            playerList[i].client.send(f"Player {x+1} is currently on fold\n".encode())
                        playerList[i].client.send(f"Player {x+1} has {playerList[x].money}, currently betting {playerList[x].currentBet}\n".encode())
                playerList[i].client.send(f"You have {playerList[i].money} chips\n".encode())
                playerList[i].client.send(f"\nPlayer {i+1}, what would you like to do?\n".encode())
                playerList[i].client.send(f"[Fold]   [Call]({highestBet})    [Call Any]\n".encode())
                playerList[i].client.send("input".encode())
                playerAction=playerList[i].client.recv(1024).decode("utf-8")
                if playerAction.lower()=="call":
                    if playerList[i].money>=highestBet-playerList[i].currentBet:
                        playerList[i].money-=highestBet-playerList[i].currentBet
                        pot+=highestBet-playerList[i].currentBet
                        playerList[i].currentBet+=highestBet-playerList[i].currentBet
                        playerList[i].client.send(f"You called {playerList[i].currentBet}\n".encode())
                        for p in playerList:
                            p.check=True
                            if p.client!=playerList[i].client:
                                p.client.send(f"Player {i+1} called {playerList[i].currentBet}\n".encode())
                        print(f"Player {i+1} called {playerList[i].currentBet}")
                    else:
                        pot+=playerList[i].money
                        playerList[i].client.send(f"You called {playerList[i].money}\n".encode())
                        playerList[i].currentBet+=playerList[i].money
                        for p in playerList:
                            if p.client!=playerList[i].client:
                                p.client.send(f"Player {i+1} called {playerList[i].currentBet}\n".encode())
                        print(f"Player {i+1} called {playerList[i].currentBet}")
                        playerList[i].money=0
                elif playerAction.lower()=="call any":
                    if playerList[i].money<=highestBet:
                        playerList[i].client.send("You have less chips than the current highest bet, putting the rest of your chips in...\n".encode())
                        pot+=playerList[i].money
                        playerList[i].client.send(f"You called {playerList[i].money}\n".encode())
                        for p in playerList:
                            p.check=True
                            if p.client!=playerList[i].client:
                                p.client.send(f"Player {i+1} called {playerList[i].currentBet}\n".encode())
                        print(f"Player {i+1} called {playerList[i].money}")
                        playerList[i].money=0
                    else:
                        playerList[i].client.send("How much would you like to call?\n".encode())
                        playerList[i].client.send("input".encode())
                        customBet=int(playerList[i].client.recv(1024).decode("utf-8"))
                        while customBet>playerList[i].money:
                            playerList[i].client.send("You do not have that amount of chips, try again\n".encode())
                            playerList[i].lient.send("input".encode())
                            customBet=int(playerList[i].client.recv(1024).decode("utf-8"))
                        while customBet<highestBet:
                            playerList[i].client.send(f"You need to match or raise the highest bet of {highestBet}, try again\n".encode())
                            playerList[i].lient.send("input".encode())
                            customBet=int(playerList[i].client.recv(1024).decode("utf-8"))
                        pot+=customBet
                        playerList[i].money-=customBet
                        playerList[i].currentBet=customBet
                        highestBet=customBet
                        playerList[i].client.send(f"You called {customBet}\n".encode())
                        for p in playerList:
                            p.check=True
                            if p.client!=playerList[i].client:
                                p.client.send(f"Player {i+1} called {customBet}\n".encode())
                        print(f"Player {i+1} called {customBet}\n")
                elif playerAction.lower()=="fold":
                    playerList[i].fold=True
                    for p in playerList:
                            if p.client!=playerList[i].client:
                                p.client.send(f"Player {i+1} folded\n".encode())
                    print(f"Player {i+1} folded")
            elif playerList[i].money!=0 and playerList[i].fold==False and playerList[i].check==False:
                for x in range(len(playerList)):
                    playerList[x].client.send("-----------------------------------------------------------\n".encode())
                    playerList[x].client.send(f"Player {i+1}'s Turn\n".encode())
                playerList[i].client.send(displayCards().encode())
                playerList[i].client.send(f"Your cards:\n{playerList[i].getCards()}\n".encode())
                playerList[i].client.send(f"\nPot chips are {pot}\n".encode() )
                for x in range(len(playerList)):
                    if x!=i:
                        if playerList[x].fold==True:
                            playerList[i].client.send(f"Player {x+1} is currently on fold\n".encode())
                        playerList[i].client.send(f"Player {x+1} has {playerList[x].money}, currently betting {playerList[x].currentBet}\n".encode())
                playerList[i].client.send(f"You have {playerList[i].money} chips\n".encode())
                playerList[i].client.send(f"\nPlayer {i+1}, what would you like to do?\n".encode())
                playerList[i].client.send("[Fold]   [Check]    [Raise]\n".encode())
                playerList[i].client.send("input".encode())
                playerAction=playerList[i].client.recv(1024).decode("utf-8").lower()
                if playerAction=="check":
                    playerList[i].check=True
                    for p in playerList:
                        p.client.send(f"Player {i+1} checked\n".encode())
                elif playerAction=="raise":
                    playerList[i].client.send("How much more chips would you like to raise?\n".encode())
                    playerList[i].client.send("input".encode())
                    Raise = int(playerList[i].client.recv(1024).decode("utf-8"))
                    while Raise>playerList[i].money:
                        playerList[i].client.send("You do not have that amount of chips to raise, try again\n".encode())
                        playerList[i].client.send("input".encode())
                        Raise=int(playerList[i].client.recv(1024).decode("utf-8"))
                    for x in playerList:
                        x.check=False
                    print(f"Player {i+1} raised {Raise} more chips")
                    for p in playerList:
                        p.check=True
                        if p.client!=playerList[i].client:
                            p.client.send(f"Player {i+1} raised {Raise} more chips\n".encode())
                    pot+=Raise
                    playerList[i].money-=Raise
                    highestBet+=Raise
                    playerList[i].currentBet+=Raise
                elif playerAction.lower()=="fold":
                    playerList[i].fold=True
                    for p in playerList:
                            if p.client!=playerList[i].client:
                                p.client.send(f"Player {i+1} folded\n".encode())
        
        betting=False
        if winner==0:
            for p in playerList:
                if ((p.money!=0 and p.currentBet<highestBet) or p.check==False) and (p.fold==False and p.check==False):
                    betting=True
                    break

#main game
def game():
    global playerList
    global winner
    global communityCard
    global highestBet
    global rounds
    global pot
    rounds=0
    starter=-1
    
    #will loop until only one player has money left
    while True:
        if winCon():
            break
        #used for keeping track whose turn it is to go first
        starter+=1
        #reset the turn back to player 1 if it goes out of bounds
        if starter>len(playerList)-1:
            starter=0
        #rounds are for keeping track the minimum amount of bet required
        rounds+=1
        #this variable will be used for printing who wins each hand
        winner=0
        #community cards is what will be on the center of the table
        communityCard=[]
        #this is just a list to help check if a card already exists on the table or in someones hand
        allCards=[]
        #highestBet will keep track of the highest bet required to continue playing
        highestBet=100*rounds
        #all the chips that players have put in
        pot=0
        #loop for making cards in player hands along with checking if those cards exist already
        for i in playerList:
            i.fold=False
            i.card1=card(switch_hand(random.randint(0,3)), random.randint(2,14))
            while True:
                if duplicateCheck(i.card1)==False:
                    break
                i.card1=card(switch_hand(random.randint(0,3)), random.randint(2,14))
            allCards.append(i.card1)         
            i.card2=card(switch_hand(random.randint(0,3)), random.randint(2,14))
            while True:
                if duplicateCheck(i.card2)==False:
                    break
                i.card2=card(switch_hand(random.randint(0,3)), random.randint(2,14))
            allCards.append(i.card2)
            i.check=False
            i.currentBet=0
        
        #the blind betting process
        turn(starter)
        
        #first betting over, generate 3 community cards
        for i in range(3):
            temp=card(switch_hand(random.randint(0,3)), random.randint(2,14))
            while True:
                if duplicateCheck(temp)==False:
                    break
                temp=card(switch_hand(random.randint(0,3)), random.randint(2,14))
            communityCard.append(temp)
            allCards.append(temp)
        
        print("-----------------------------------------------------------")
        print("~~Flop~~")
        print("\nThe community cards are:")
        for p in playerList:
            p.client.send("-----------------------------------------------------------\n".encode())
            p.client.send("~~Flop~~\n".encode())
            p.client.send("The community cards are:\n".encode())
        for i in range(len(communityCard)):
            print(communityCard[i].getCard())
            for p in playerList:
                p.client.send(f"{communityCard[i].getCard()}\n".encode())
        print("-----------------------------------------------------------")
        
        #second betting process
        turn(starter)
        
        #add one more card to community cards
        temp=card(switch_hand(random.randint(0,3)), random.randint(2,14))
        while True:
            if duplicateCheck(temp)==False:
                break
            temp=card(switch_hand(random.randint(0,3)), random.randint(2,14))
        communityCard.append(temp)
        allCards.append(temp)
        print("-----------------------------------------------------------")
        print("~~Turnr~~")
        print("\n4th Card added, the community cards are now:")
        for p in playerList:
            p.client.send("-----------------------------------------------------------\n".encode())
            p.client.send("~~Turn~~\n".encode())
            p.client.send("4th Card added, he community cards are now:\n".encode())
        for i in range(len(communityCard)):
            print(communityCard[i].getCard())
            for p in playerList:
                p.client.send(f"{communityCard[i].getCard()}\n".encode())
        print("-----------------------------------------------------------")
        
        #the next betting process starts again
        turn(starter)
        
        #adding in the last card to community cards
        temp=card(switch_hand(random.randint(0,3)), random.randint(2,14))
        while True:
            if duplicateCheck(temp)==False:
                break
            temp=card(switch_hand(random.randint(0,3)), random.randint(2,14))
        communityCard.append(temp)
        allCards.append(temp)
        print("-----------------------------------------------------------")
        print("~~River~~")
        print("5th card added, the community cards are now:")
        for p in playerList:
            p.client.send("-----------------------------------------------------------\n".encode())
            p.client.send("~~River~~\n".encode())
            p.client.send("5th carded added, the community cards are now:\n\n".encode())
        for i in range(len(communityCard)):
            print(communityCard[i].getCard())
            for p in playerList:
                p.client.send(f"{communityCard[i].getCard()}\n".encode())
        print("-----------------------------------------------------------")
        
        #last betting process before hand comparison
        turn(starter)
        
        print("Showdown!")
        for p in playerList:
            p.client.send("-----------------------------------------------------------\n".encode())
            p.client.send("~~Showdown!~~\n".encode())
            p.client.send("The community cards are:\n".encode())
        print("The community cards are:\n")        
        
        #bunch of printing here
        for i in range(len(communityCard)):
            print(communityCard[i].getCard())
            for p in playerList:
                p.client.send(f"{communityCard[i].getCard()}\n".encode())
    
        for i in range(len(playerList)):
            if playerList[i].fold==False:
                print(f"Player {i+1} has the following cards:\n{playerList[i].getCards()}\n")
                for p in playerList:
                    p.client.send(f"Player {i+1} has the following cards:\n{playerList[i].getCards()}\n".encode())
        
        #hand comparison should go here
        if winner==0:
            print("The dealer will now decide the winner")
            for p in playerList:
                p.client.send("The dealer will now decide the winner\n".encode())
            winner=int(input())
        print(f"Player {winner} won this hand!\n")
        for p in playerList:
            p.client.send(f"Player {winner} won this hand!\n".encode())
        playerList[winner-1].money+=pot

winner = 0
playerList=[]
communityCard = []
allCards=[]

highestBet=100
pot=0

s=socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 1234))
s.listen(10)

print("Welcome to Poker Simulator, each player begins with 10000 chips")
print("\nDisclaimer:\nThe winner of each round will be determined by the dealer(You) MANUALLY")
print("The winner of each hand will get ALL the money in the pot\n")
print("As the dealer, you will be deciding who wins each hand, please wait for the line: \n(The dealer will now decide the winner)")

while True:
    print("\nWaiting for clients to join...\n")
    clientsocket, address = s.accept()
    print(f"Connection from {address} has been established.")
    playerList.append(player(clientsocket))
    print(f"Current player amount: {len(playerList)}")
    if len(playerList)>1:
        start=input("Minimum amount of players acquired. Start Game?(Enter y/n)")
        if start.lower()=="y":
            break

print("Game Started, player actions will be available to view here...")
for p in playerList:
    p.client.send("Game Started! Please wait for your turn\n".encode())
game()
for p in playerList:
    p.client.send(f"Player {winnerCheck()} has won the game! Thank you for playing".encode())
    p.client.send("exit".encode())
print(f"Player {winnerCheck()} has won the game! Thank you for playing")

s.close()
