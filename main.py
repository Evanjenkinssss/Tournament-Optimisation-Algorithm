import time
import argparse
import random 
import math

def read_tournament(file_path):
    #function to read the tournament data from the file
    tournament = []
    names = {}
    initialrank = []
    try:
        with open(file_path, 'r') as file:
            participants_num = int(file.readline().strip())

            for x in range(participants_num):
                participant_number, participant_name = file.readline().strip().split(',', 1)
                names[int(participant_number)] = participant_name
                initialrank.append(participant_name)

            file.readline()
            #Read edges 
            for line in file:
                weight, edge = line.strip().split(',', 1)
                participant1, participant2 = map(int, edge.split(','))

                tournament.append((int(weight), names[participant1], names[participant2]))

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
        return None


    return tournament, initialrank



def kemeny_score(ranking, tournament):
    #initialise disagremeent count (ie kemeny score)
    disagreements = 0
    #create rank map
    rank_map = {name: rank for rank, name in enumerate(ranking)}

    #loop through tournament
    for weight, winner, loser in tournament:
        #if the loser is higher ranked than winner (the winner has a higher index in rankmap)
        if rank_map[winner] > rank_map[loser]:
            #add the weight to disagreements
            disagreements += weight

    return disagreements

def adjusted_kemeny_score(old_rank_map, new_rank_map, original_score, original_ranking, neighbor_ranking, idx1, idx2, tournament):
    adjusted_score = original_score

    #Map names to ranks for original and neighbor rankings
    original_rank_map = old_rank_map.copy()
    neighbor_rank_map = new_rank_map.copy()

    #Determine the range of participants which are affected
    affected_range = set(neighbor_ranking[min(idx1, idx2):max(idx1, idx2) + 1])

    for weight, winner, loser in tournament:
        if winner in affected_range or loser in affected_range:
            #Use the predone rank maps
            original_winner_rank = original_rank_map[winner]
            original_loser_rank = original_rank_map[loser]
            new_winner_rank = neighbor_rank_map[winner]
            new_loser_rank = neighbor_rank_map[loser]

            #Compare the ranks to determine score adjustment
            if (original_winner_rank > original_loser_rank) != (new_winner_rank > new_loser_rank):
                if new_winner_rank > new_loser_rank:
                    adjusted_score += weight 
                else:
                    adjusted_score = adjusted_score - weight

    return adjusted_score

def neighborhood(ranking, rank_map):
    #gset neighbour to ranking 
    neighbour = ranking.copy()
    old_rank_map = rank_map.copy()  #copy original rank map

    idx1, idx2 = random.sample(range(len(neighbour)), 2)

    #Swap the participants in the ranking
    neighbour[idx1], neighbour[idx2] = neighbour[idx2], neighbour[idx1]

    #uppdate the rank map with the new indices
    new_rank_map = rank_map.copy()
    new_rank_map[neighbour[idx1]], new_rank_map[neighbour[idx2]] = new_rank_map[neighbour[idx2]], new_rank_map[neighbour[idx1]]

    return neighbour, idx1, idx2, old_rank_map, new_rank_map


def simulated_annealing(rank_map, tournament, initial_temp, temp_length, cooling_ratio, num_no_improve, initial_rank):
    #SA algorithm
    rank_map = rank_map.copy()
    
    #Set current ranking to the initial solution of the given tournament
    current_ranking = initial_rank
    
    #Initialise best rank as the initial solution
    best_rank = current_ranking.copy()

    #Defining of variables
    current_temp = initial_temp
    no_improvement_count = 0

    current_cost = kemeny_score(current_ranking, tournament)
    bestrankkemeny = current_cost

    #While loop which checks whether temp and no improvment counts are above the thresholds 
    while current_temp > 0.1  and no_improvement_count < num_no_improve:

        #Iterate for length of temp length 
        for x in range(temp_length):
            #Define the neighbour
            neighbour_rank, idx1, idx2, old_rank_map, new_rank_map = neighborhood(current_ranking, rank_map)

            #Calculatye costs of current ranking and neighbour ranking

            neighbour_cost = adjusted_kemeny_score(old_rank_map, new_rank_map, current_cost, current_ranking, neighbour_rank, idx1,idx2, tournament)

            #If the neighbour cost is lower than current cost or random acceptance probability 
            if current_cost > neighbour_cost or random.uniform(0,1) < math.exp((current_cost - neighbour_cost) / current_temp):
                #The set the neighbouring rank to the current rank, make the change 
                current_ranking = neighbour_rank.copy()
                rank_map = new_rank_map.copy()
                current_cost = neighbour_cost

                #If neighbouring cost beats the best rank cost
                if neighbour_cost < bestrankkemeny:
                    #set the neighbour as the best rank

                    best_rank = current_ranking.copy()
                    bestrankkemeny = neighbour_cost

                    #reset no improvement count
                    no_improvement_count = 0
            else:
                #increment no improvement count 
                no_improvement_count += 1

        current_temp *= cooling_ratio

        

    
    return best_rank, bestrankkemeny


def main():
    #parser
    parser = argparse.ArgumentParser()
    parser.add_argument('file_path', type=str)

    args = parser.parse_args()
    file_path = args.file_path

    
    #read the tournament data from the file
    tournament, initial_rank = read_tournament(file_path)

    rank_map = {name: rank for rank, name in enumerate(initial_rank)}
    initial_temp = 75 #initial temperature
    temp_length = 200 #temperature length
    cooling_ratio = 0.80 #cooling ratio
    num_no_improve = 1000 #stopping criteria 

    #start time
    start_time = time.time()
   
    #simulated annealing
    best_ranking, bestkemeny = simulated_annealing(rank_map,tournament, initial_temp, temp_length, cooling_ratio, num_no_improve, initial_rank)

    #end time
    end_time = time.time()

    #print best rank and kemeny score
    print("Best Ranking:", best_ranking)
    print("Kemeny Score:", bestkemeny)

    #Print runtime in ms  
    print("Runtime (ms):", int((end_time - start_time) * 1000))

if __name__ == "__main__":
    main()