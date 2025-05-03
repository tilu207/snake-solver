from game.game import Game
from solvers.solver import Solver
import numpy as np


def evaluate(game: Game, solvers: list[Solver], num_of_games: int, save_path: str = "", log: bool = False) -> dict:
    """
    Evaluates a list of Snake solvers by running multiple games for each and collecting statistics.
    Optionally, the progress can be logged and the results may be saved in a txt.
    Returns a dictionary containing the statistics.
    """
    def _get_score_over_time(game_dict):
        data = []

        apple_index = 0

        for i, move in enumerate(game_dict['move_history']):
            if move == game_dict['apple_history'][apple_index]:
                apple_index += 1
                data.append((3 + apple_index, i+1))

        return data

    grid_size = game.get_grid_size()
    stats = {}

    rows = [["Solver", "Avg Moves", "Min Moves", "Max Moves", "Std Moves", "Avg Score", "Completion (%)", "Avg Time per Game (sec)"]]

    # play games
    for solver in solvers:
            if log:
                print(f"Starting to evaluate solver {solver.name}.")
            
            stats[solver.name] = {}
            all_scores = []
            all_moves = []
            all_total_time = []
            all_scores_over_time = []
            games_completed = 0


            for i in range(num_of_games):
                if log:
                    print(f"Running game {solver.name} - {i+1}/{num_of_games}.")
                game_dict = game.play_game(solver)
                all_scores_over_time.append(_get_score_over_time(game_dict))
                all_scores.append(game_dict['snake_length'])
                all_moves.append(game_dict['total_moves'])
                all_total_time.append(game_dict['total_time'])
                games_completed += 1 if game_dict['game_over_reason'] == "Reached max length." else 0
                solver.reset()

            max_score = max(len(scores) for scores in all_scores_over_time) + 3
            average_scores_over_time = np.zeros(max_score)
            count_at_moves = np.zeros(max_score)

            for score_over_time in all_scores_over_time:
                for score, move_num in score_over_time:
                    score_idx = score - 1
                    average_scores_over_time[score_idx] += move_num
                    count_at_moves[score_idx] += 1

            for i in range(max_score):
                if count_at_moves[i] > 0:
                    average_scores_over_time[i] /= count_at_moves[i]

            avg_moves = round(np.mean(all_moves) , 2)
            min_moves = np.min(all_moves) 
            max_moves = np.max(all_moves)
            std_moves = round(np.std(all_moves), 2)
            avg_score = round(np.mean(all_scores), 2)
            completion_rate = round((games_completed / num_of_games) * 100, 2)
            avg_time_per_game = round(np.mean(all_total_time) , 2)

            stats[solver.name]['average_scores_over_time'] = average_scores_over_time
            stats[solver.name]['avg_moves'] = avg_moves
            stats[solver.name]['min_moves'] = min_moves
            stats[solver.name]['max_moves'] = max_moves
            stats[solver.name]['std_moves'] = std_moves
            stats[solver.name]['completion_rate'] = completion_rate
            stats[solver.name]['avg_time_per_game'] = avg_time_per_game

            rows.append([solver.name, avg_moves, min_moves, max_moves, std_moves, avg_score, completion_rate, avg_time_per_game])

    col_widths = [max(len(str(row[i])) for row in rows) + 2 for i in range(len(rows[0]))]

    if log:
        print(f"{num_of_games} game(s) on a {grid_size[0]}x{grid_size[1]} grid.")
        for row in rows:
            print("".join(str(col).ljust(col_widths[i]) for i, col in enumerate(row)))

    if save_path:
        with open(save_path, "w") as f:
            for row in rows:
                f.write("".join(str(col).ljust(col_widths[i]) for i, col in enumerate(row)) + "\n")

    return stats