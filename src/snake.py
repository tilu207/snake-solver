"""
Main entry point for executing and evaluating Snake solvers.

Supports three modes:
- 'single': Runs a single game with a specified solver.
- 'eval': Evaluates multiple solvers over several games and outputs performance metrics.
- 'visualize': Visualize a previously played game.

Solvers can be dynamically configured using a JSON file.
"""

import argparse
import json
import sys
import importlib
import matplotlib.pyplot as plt

from game.game import Game
from utils.evaluate import evaluate


def main():
    parser = argparse.ArgumentParser(description="Run with mode and config file.")
    parser.add_argument("-mode", type=str, help="The mode to run (single, eval or visualize).")
    parser.add_argument("-config_path", type=str, help="Path to the JSON config file (or game file when visualizing)")
    parser.add_argument("-plot", action="store_true", help="Saves a plot of the Avg Moves over time. Only for eval mode.")
    parser.add_argument("-log", action="store_true", help="Enable logging throughout evaluation.")

    args = parser.parse_args()

    try:
        with open(args.config_path, "r") as f:
            config = json.load(f)
    except FileNotFoundError:
        print(f"Error: File not found at '{args.config_path}'")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Failed to parse JSON in config file '{args.config_path}'")
        sys.exit(1)

    # Run logic based on mode
    if args.mode == "eval":
        run_eval(config, args.log, args.plot)
    elif args.mode == "single":
        run_single_run(config, args.log)
    elif args.mode == "visualize":
        from visualize.visualizer import visualize
        visualize(config)
    else:
        print(f"Error: Unknown mode '{args.mode}'")
        sys.exit(1)

def run_eval(config, log, plot):
    print("Evaluating given solvers.")
    
    grid_size = config['grid_size']
    num_of_games = config['num_of_games']

    solvers = []

    for solver_config in config['solvers']:
        solvers.append(create_solver(solver_config, grid_size))

    game = create_game(config)
    result = evaluate(game, solvers, num_of_games, log=log, save_path=config['save_path'])

    if plot:
        plot_score_over_time(result, config['plot_path'])

    print("Evaluation completed and results saved.")

def run_single_run(config, log):
    print("Running single game with given solver.")
    game = create_game(config)
    solver = create_solver(config['solver'], config['grid_size'])
    game.play_game(solver, save_path=config['save_path'], log=log)
    print("Game completed and saved.")

def create_solver(solver_config, grid_size):
    solvers_module = importlib.import_module("solvers." + solver_config["module_name"])
    SolverClass = getattr(solvers_module, solver_config["class_name"])

    solver = SolverClass(solver_config['name'], grid_size)

    for key, value in solver_config['parameters'].items():
        setattr(solver, key, value)

    return solver

def create_game(config):
    game = Game(config['grid_size'])

    if "max_moves" in config.keys():
        game.max_moves = config['max_moves']
    if "seed" in config.keys():
        game.set_seed(config['seed'])

    return game

def plot_score_over_time(result, plot_path):
    plt.figure(figsize=(10, 6))

    for solver_name in result.keys():
        values = result[solver_name]['average_scores_over_time']
        plt.plot(range(1, len(values) + 1), values, label=solver_name)

    plt.title("Avg Moves per Score")
    plt.xlabel("Score")
    plt.ylabel("Avg Moves")
    plt.legend(title="Solvers")
    plt.grid(True)

    plt.savefig(plot_path)

if __name__ == "__main__":
    main()
