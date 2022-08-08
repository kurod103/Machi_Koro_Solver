"""MACHI KORO STRATEGIES"""
import random
import pandas
import os 
dir_path = os.path.dirname(os.path.realpath(__file__))
os.chdir(dir_path)

dataset = pandas.read_csv("Card_Yields.csv")
#Initialize Game State
from Machi_Koro_Params import strat
from Machi_Koro_Params import turns
from Machi_Koro_Params import Players
from Machi_Koro_Params import Population
from Machi_Koro_Params import iterations

from Machi_Koro_Params import Genetic_Algorithm
from Machi_Koro_Params import genetic_iterations

from Machi_Koro_Params import Monte_Carlo
from Machi_Koro_Params import Monte_Carlo_Table
from Machi_Koro_Params import Monte_Carlo_Table_2
from Machi_Koro_Params import monte_carlo_iterations

from Machi_Koro_Params import Strategy_Tester
from Machi_Koro_Params import test_iterations

#User input; generate strategy sets, or test strategies

#Pandas Dataframe: Roll/Card#, Value

global Money


Costs=[1,1,3,6,3,1,2,5,3,2,2,3,6,7,8,4,10,16,22]

Item_Dict = ["Wheat Field","Ranch","Forest","Mine","Apple Orchard","Bakery","Convenience Store",
             "Cheese Factory","Furniture Factory","Fruit and Vegetable Market","Cafe",
             "Family Restaurant","Stadium","TV Station","Business Center","Station","Shopping Mall",
             "Amusement Park","Radio Station"]

"""GAME FUNCTIONS"""
#Reset a list of values, adding up each card for each player
def compile_player_values(cards_list):
    values_list = [[0]*24 for i in range(Players)]
    for player in range(len(cards_list)):
        for card in range(len(cards_list[player])):
            card_count = cards_list[player][card] #examine single card
            if card_count > 0:
                for i in range(card_count):
                    values_list =add_card(player,card,cards_list,values_list)
    return values_list

#Add the value of a card to a player's value function
def add_card(player,card,cards_list,values_list):
    if card<7: #Base Industries
        card_yield = dataset.iloc[card][1:].tolist()
        for i in range(len(values_list[player])):
            values_list[player][i]+=card_yield[i]        
            if  card >=5:#Bakery and Convenience Store
                if card_yield[i] > 0 and cards_list[player][16] > 0: #If Shopping Mall
                    values_list[player][i] +=1
                    
    elif card==7: #Cheese Factory
        values_list[player][6]+=(cards_list[player][1]*3)#on rolling a 7, your turn
        
    elif card==8: #Furniture Factory
        values_list[player][9]+=(cards_list[player][2]*3+cards_list[player][3]*3) #On rolling an 8
        
    elif card==9: #Fruit and Vegetable Market
        values_list[player][10]+=(cards_list[player][0]*2+cards_list[player][4]*2)#Value for 11
        values_list[player][11]+=(cards_list[player][0]*2+cards_list[player][4]*2)#Value for 12
        
    elif card==10: #Cafe
        values_list[player][14]+=1 #When the other player rolls a 3
        if cards_list[player][16]>0:#If Shopping Mall
            values_list[player][14]+=1
        for i in range(len(values_list)): #Reduce value of other player rolling a 3
            if i != player:
                values_list[i][2]-=1
                if cards_list[player][16]>0:#If Shopping Mall
                    values_list[i][2]-=1

            
    elif card==11: #Family Restaurant
        values_list[player][20]+=2 #When the other player rolls a 9
        values_list[player][21]+=2 #When the other player rolls a 10
        if cards_list[player][16]>0:#If Shopping Mall
            values_list[player][20]+=1
            values_list[player][21]+=1
        for i in range(len(values_list)): #Reduce value of other player rolling a 9 or 10
            if i != player:
                values_list[i][8]-=2
                values_list[i][9]-=2
                if cards_list[player][16]>0:#If Shopping Mall
                    values_list[i][8]-=1
                    values_list[i][9]-=1
                    
    elif card==12: #Stadium
        values_list[player][5]+=2*(Players-1) #on 6 roll, gain 2 from all other players
        for i in range(len(values_list)): #All other players lose 2 coins
            if i != player:
                values_list[i][17]-=2
                
    elif card==13: #TV Station
        values_list[player][5]+=3 #on 6 roll, receive 3 coins from one player
        
        #Check for the best player
        best_sum= 0
        best_player = 0
        for i in range(Players):
            if i != player:
                this_sum = sum(values_list[i]) #Not a perfect measure, but pretty close
                if this_sum>best_sum:
                    best_sum = this_sum
                    best_player = i #This is who we will take money from
        values_list[best_player][17]-=3
        
    elif card==14: #Business Center
        pass
        #This card is honsetly very impractical. If anyone finds this comment
        #and wants me to code in a real business center card, I can do so. I do not
        #think that any real strategy should ever waste 8 coins on this however.
    return values_list

#Roll the Dice, checks for doubles, radio tower, etc
def roll_dice(values,landmarks):
    train_station = landmarks[0]
    amusement = landmarks[2]
    radio= landmarks[3]
    
    
    best_value = values.index(max(values))
    second_dice = False
    second_roll = 0
    
    if best_value>5 and best_value<12: #If your best value is over 6, then definitely roll 2 dice
        if train_station:
            second_dice = True
    roll = random.randint(1,6)
    if second_dice:
        second_roll = random.randint(1,6)
    
    if radio and values[roll]<=2: #re roll with radio tower if you get 0
        roll= random.randint(1,6)
        if second_dice:
            second_roll= random.randint(1,6)
    
    if amusement:
        if roll==second_roll:
            return roll+second_roll, True
    
    return roll+second_roll, False
    
#Checks the value one player receives from this roll
def dice_yield(roll, values, your_turn=True):
    if your_turn: #this allows us to store values/costs you incur on your turn, vs any other turn
        return values[roll-1]
    return values[roll+11]

#Can you purchase the next item on your shopping list?
def buy_check(shopping_list,cards, money):
    end_game=0
    
    for i in range(4):
        if cards[15+i]==0:
            end_game+=Costs[15+i]
    if money >=end_game:
        shopping_list = []
    if len(shopping_list)>0:
        item = shopping_list[0]
        while Card_Num[item]<1:
            shopping_list = shopping_list[1:]
            if shopping_list==[]:
                break
            item=shopping_list[0]

    else:
        #Just start adding the victory cards if nothing else
        for i in range(4):
            if cards[15+i]==0:#Add victory cards that you do not have
                shopping_list.append(15+i)
        if len(shopping_list)==0: #if its still empty, just add random cards
            shopping_list.append(random.randint(0,14))
        item = shopping_list[0]
    if Costs[item] > money:
        return False, shopping_list, cards, money
    else:
        Card_Num[item]-=1
        shopping_list=shopping_list[1:]
        cards[item] +=1
        money-= Costs[item]
    return item, shopping_list, cards,money

#Plays one round of Machi Koro
def Take_Turn(p,Cards_List,Values_List,Landmarks):
    roll,double = roll_dice(Values_List[p],Landmarks[p])
    
    for i in range(Players):
        if i ==p: 
            Money[i]+= dice_yield(roll,Values_List[i])
        else: Money[i]+= dice_yield(roll,Values_List[i],False)
    
    if monte_carlo_iterations==1 and Monte_Carlo:
        print("rolling...",roll)
        for i in range(Players):
            if p ==i : print(dice_yield(roll,Values_List[p]), Money[i])
            else: print(dice_yield(roll,Values_List[i],False), Money[i])
            
    bought,Strategy[p],Cards_List[p],Money[p]=buy_check(Strategy[p],Cards_List[p],Money[p])
    if bought!=False:
        if monte_carlo_iterations==1 and Monte_Carlo: print("player",p+1, "bought a",Item_Dict[bought], "and now has", Money[p])
        Values_List = add_card(p,bought,Cards_List,Values_List)
        if bought>=15:
            Landmarks[p][bought-15]=True
        if bought ==16:
            Values_List=compile_player_values(Cards_List) 
            #Recalculate if a shopping mall enters play
        if all(Landmarks[p]):
            return Cards_List, Values_List, Landmarks, False, True
    return Cards_List, Values_List, Landmarks, double,  False

def Take_Turn_Fake(p,Cards_List,Values_List,Landmarks):
    roll,double = roll_dice(Values_List[p],Landmarks[p])
    
    for i in range(Players):
        if i ==p: 
            Money[i]+= dice_yield(roll,Values_List[i])
        else: Money[i]+= dice_yield(roll,Values_List[i],False)
        
    
    bought,Strategy[p],Cards_List[p],Money[p]=buy_check(Strategy[p],Cards_List[p],Money[p])
    if bought!=False:
        if monte_carlo_iterations==1 and Monte_Carlo: print("player",p+1, "bought a",Item_Dict[bought], "and now has", Money[p])
        Values_List = add_card(p,bought,Cards_List,Values_List)
        if bought>=15:
            Landmarks[p][bought-15]=True
        if bought ==16:
            Values_List=compile_player_values(Cards_List) 
            #Recalculate if a shopping mall enters play
    return Cards_List, Values_List, Landmarks, double,  False


"""REPORTS"""
#Makes the card list easier to read
def Card_Report(cards):
    cards_list=[]
    for card in range(len(cards)):
        if cards[card]>0:
            cards_list.append(str(Item_Dict[card])+" x "+str(cards[card]))    
    return cards_list


"""GENETIC ALGO"""
def mutate_strategy(strategy):
    mutate_type = random.randint(0,4)
    if len(strategy)==0:
        return [random.randint(0,18)]
    elif mutate_type == 0: #Change one value
        random_card = random.randint(0,18)
        if random_card in strategy and random_card>=15:
            return strategy
        strategy[random.randint(0,len(strategy)-1)]=random_card
    elif mutate_type == 1: #Add a random value in a random place
        insert_point = random.randint(0,len(strategy)-1)
        if strategy[insert_point]>=15:
            return strategy
        strategy.insert(insert_point,strategy[insert_point])
    elif mutate_type == 2: #Remove a random value
        strategy.pop(random.randrange(len(strategy)))
    elif mutate_type==3: #Add a random value to the end
        random_card = random.randint(0,18)
        if random_card >=15:
            if random_card in strategy:
                return strategy
        strategy.append(random_card)
    else: strategy.pop() #remove 
    return strategy

def advanced_mutate(strategy_1, strategy_2):
    cut = random.randint(0,min(len(strategy_1),len(strategy_2)))
    strategy_1= strategy_1[:cut] + strategy_2[cut:]
    return strategy_1


"""GENETIC ALGORITHM--WHAT WILL DO WELL AGAINST Y STRATEGY"""

Fitnesses = [0]*Population
Strategies = [strat[random.randint(0,len(strat)-1)] for i in range(Population)]

for genetic_iteration in range(genetic_iterations):
    if Genetic_Algorithm==False:
        break
    Strategy =[]
    Initial_Strategies=[]
    Strategy=[strat[7]]
    Initial_Strategies = [strat[7]]
    for i in range(Players-1):
        add_strategy = Strategies[random.randint(0,len(Strategies))-1]
        Strategy.append(add_strategy)
        Initial_Strategies.append(add_strategy)
    
    wins = [0]*Players
    
    for iteration in range(iterations):
        Card_Num= [6]*19

        Cards_List = []
        
        for i in range(Players):
            Cards_List.append([0]*19)
            Cards_List[-1][0]=1
            Cards_List[-1][5]=1
            
            Strategies[i]=Initial_Strategies[i]
        
        Values_List = compile_player_values(Cards_List)
        
        Money=[3]*Players
        Landmarks=[[False,False,False,False]]*Players
        
        Ended_Game = False
        for turn in range(turns):
            if Ended_Game:
                break
            for p in range(Players):
                doubles=False
                bought = False
                
                Cards_List, Values_List, Landmarks, Doubles, Ended_Game = Take_Turn(p,Cards_List,Values_List,Landmarks)
                while Doubles: #If you have an amusement park and roll doubles, keep going!
                    Cards_List, Values_List, Landmarks, Doubles, Ended_Game = Take_Turn(p,Cards_List,Values_List,Landmarks)
                
                if Ended_Game:    
                    wins[p] +=1
                    break
    for p in range(Players): #Update the win rate of each strategy
        win_rate=wins[p]/(sum(wins))
        try:
            Strategy_num = Strategies.index(Initial_Strategies[p])
            Fitnesses[Strategy_num] = win_rate 
        except: pass
    win_index = Initial_Strategies[wins.index(max(wins))]
    winner = Strategies.index(win_index)
    
    if genetic_iteration%10 ==0:
        print(Fitnesses)
        print(Strategies[winner], Fitnesses[winner])
        
    if random.randint(0,1)==1:
        Strategies.append(Strategies[winner])
        Fitnesses.append(Fitnesses[winner])
    
    if random.randint(0,1)==1:
        Fitnesses.append(0)
        Strategies.append(mutate_strategy(Strategies[winner]))
    
    if random.randint(0,10)==1:
        Strategies.append(strat[random.randint(0,7)])
        Fitnesses.append(0)
    
    if len(Strategies)<Population/2-1:
        while len(Strategies)<Population:
            Strategies.append(advanced_mutate(strat[random.randint(0,7)],strat[random.randint(0,7)]))
            Fitnesses.append(0)
    if len(Strategies)>Population+10:  
        while len(Strategies)>Population/2:
            loser = Fitnesses.index(min(Fitnesses))
            Fitnesses.pop(loser)
            Strategies.pop(loser)
    #print(genetic_iteration)

if Genetic_Algorithm: print(Strategies)


"""MONTE CARLO SIMULATION--HOW MUCH WILL X STRATEGY BEAT Y STRATEGY"""

winning_turns = [] #Record winning turns from each strategy


def Monte_Carlo_Run(Strategy_List):
    won_games = 0
    wins = 0
    for iteration in range(monte_carlo_iterations):
        
        global Card_Num
        Card_Num= [6]*19
        
        Cards_List = []
        
        global Strategy
        Strategy=[]
        
        for i in range(Players):
            if Strategy_List[i]=="random_strategy":
                Strategy.append(strat[random.randint(0,len(strat)-1)])
            elif Strategy_List[i]=="true_random":
                Strategy.append([random.randint(0,12) for i in range(8)])
            else:
                Strategy.append(Strategy_List[i])
            
            Cards_List.append([0]*19)
            Cards_List[-1][0]=1
            Cards_List[-1][5]=1
        Values_List = compile_player_values(Cards_List)
        
        
        
        global Money
        Money=[3]*Players
        Landmarks=[[False,False,False,False]]*Players
        
        Ended_Game = False
        for turn in range(turns):
            if Ended_Game:
                break
            if monte_carlo_iterations ==1:
                print("TURN ", turn)
                print(Values_List)
                print(Card_Report(Cards_List[0]))
                print(Card_Report(Cards_List[1]))
                print()
            
            for p in range(Players):
                doubles=False
                bought = False
                
                
                Cards_List, Values_List, Landmarks, Doubles, Ended_Game = Take_Turn(p,Cards_List,Values_List,Landmarks)
                while Doubles: #If you have an amusement park and roll doubles, keep going!
                    Cards_List, Values_List, Landmarks, Doubles, Ended_Game = Take_Turn(p,Cards_List,Values_List,Landmarks)
    
                if Ended_Game:
                    if p==0:
                        wins+=1
                    won_games+=1
                    break
    return wins, won_games

if Monte_Carlo: 
    strategy_list = [strat[1],strat[7],"random_strategy","random_strategy"]
    
    wins,won_games = Monte_Carlo_Run(strategy_list)
    win_rate = (wins/won_games)*100
    print("The win rate of this strategy is:",win_rate,"%")

if Monte_Carlo_Table:
    Players = 2
    
    strategy_wins = []
    for strategy_1 in strat:
        strategy_wins.append([])
        for strategy_2 in strat:
            strategy_list=[strategy_1,strategy_2]
            wins,won_games = Monte_Carlo_Run(strategy_list)
            
            win_rate = (wins/won_games)
            strategy_wins[-1].append(win_rate)
    strategy_wins = pandas.DataFrame(strategy_wins)
    
    #strategy_wins.columns = ["One Die Spread","Convenience Store","Fruit and Veg","Furniture Factory","Mine Spread","Bakery","Buy Nothing","Cheese Factory"]
    #strategy_wins.index = ["One Die Spread","Convenience Store","Fruit and Veg","Furniture Factory","Mine Spread","Bakery","Buy Nothing","Cheese Factory"]
    print(strategy_wins)
    strategy_wins.to_csv('strategy_table_2.csv')
"""       
if Monte_Carlo_Table_2:
    players_wins=[]
    for strategy in strat:
        players_wins.append([])
        for i in (range(2,5)): #Test out win times on random players in this range
            Players = i
            strategy_list=[strategy,"random_strategy","random_strategy","random_strategy"]
            wins,won_games = Monte_Carlo_Run(strategy_list)
            
            win_rate = (wins/won_games)
            players_wins[-1].append(win_rate)
    players_wins = pandas.DataFrame(players_wins)
    
    players_wins.columns=["2 players","3 players","4 players"]
    #players_wins.index = [["One Die Spread","Convenience Store","Fruit and Veg","Furniture Factory","Mine Spread","Bakery","Buy Nothing","Cheese Factory"]]
    players_wins.index=[["One Die Spread","Convenience Store","Bakery","Cheese Factory"]]
    print(players_wins)
    players_wins.to_csv('player_wins_table_2.csv')

"""    
if Monte_Carlo_Table_2:
    Players = 3
    players_wins=[]
    for strategy_1 in strat:
        players_wins.append([])
        for strategy_2 in strat:
            for strategy_3 in strat:
                strategy_list=[strategy_1,strategy_2,strategy_3,"random_strategy"]
                wins,won_games = Monte_Carlo_Run(strategy_list)
                
                win_rate = (wins/won_games)
                players_wins[-1].append(win_rate)
    players_wins = pandas.DataFrame(players_wins)
    
    #players_wins.columns=["2 players","3 players","4 players"]
    #players_wins.index = [["One Die Spread","Convenience Store","Fruit and Veg","Furniture Factory","Mine Spread","Bakery","Buy Nothing","Cheese Factory"]]
    #players_wins.index=[["One Die Spread","Convenience Store","Bakery","Cheese Factory"]]
    print(players_wins)
    players_wins.to_csv('player_wins_table_3.csv')
"""STRATEGY TESTER--HOW MANY TURNS WILL EACH STRATEGY TAKE TO WIN?"""



for strategy in strat:
    winning_turn = []
    if Strategy_Tester == False:
            break
    for iteration in range(test_iterations):
        
        Card_Num= [6]*19
        Cards_List = []
        
        for i in range(Players):
            Cards_List.append([0]*19)
            Cards_List[-1][0]=1
            Cards_List[-1][5]=1
        Values_Reset = [[0]*24 for i in range(Players)]
        Values_List = compile_player_values(Cards_List)
            
        P1_Strat = strategy
        Null_Strat = [random.randint(0,12)]*8
        
        Strategy=[P1_Strat,Null_Strat]
        
        Money=[3]*Players
        Landmarks=[[False,False,False,False]]*Players
        
        Ended_Game = False
        
        for turn in range(turns):
            if Ended_Game:
                break
            for p in range(Players):
                doubles=False
                bought = False
                
                if p==1:
                    Cards_List, Values_List, Landmarks, Doubles, Ended_Game = Take_Turn_Fake(p,Cards_List,Values_List,Landmarks)
                    
                    while Doubles: #If you have an amusement park and roll doubles, keep going!
                        Cards_List, Values_List, Landmarks, Doubles, Ended_Game = Take_Turn_Fake(p,Cards_List,Values_List,Landmarks)
                
                else:
                    Cards_List, Values_List, Landmarks, Doubles, Ended_Game = Take_Turn(p,Cards_List,Values_List,Landmarks)
                    
                    while Doubles: #If you have an amusement park and roll doubles, keep going!
                        Cards_List, Values_List, Landmarks, Doubles, Ended_Game = Take_Turn(p,Cards_List,Values_List,Landmarks)
                
                
                if Ended_Game:
                    winning_turn.append(turn)
                    break
    if Strategy_Tester:
        print("Strategy",strategy," won in: ", sum(winning_turn)/test_iterations)
        print()
    winning_turns.append(winning_turn)
    
if Strategy_Tester:
    
    turn_time = pandas.DataFrame(winning_turns)
    turn_time = turn_time.transpose()
    turn_time.columns = ["One Die Spread","Convenience Store","Fruit and Veg","Furniture Factory","Mine Spread","Bakery","Buy Nothing","Cheese Factory"]

    turn_time.to_csv('turn_times.csv')