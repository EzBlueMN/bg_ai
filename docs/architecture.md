```mermaid

classDiagram

direction TB

class Experiment {
    +run()
    +collect_metrics()
}

class Simulation {
    +seed
    +run_episode()
}

class Game {
    <<abstract>>
    +initial_state(seed)
    +legal_actions(state, player_id)
    +next_state(state, action, rng)
    +is_terminal(state)
    +evaluate_terminal(state)
}

class State {
    <<immutable>>
    +current_player
    +hash()
    +canonicalize()
}

class Action {
    <<value object>>
}

class Agent {
    +select_action(state, legal_actions)
    +on_episode_start()
    +on_step(state, action)
    +on_episode_end(outcome)
}

class Policy {
    <<interface>>
    +choose(state, legal_actions)
}

class Memory {
    <<abstract>>
    +record(state, action, outcome)
    +estimate(state, action)
    +update()
}

class Outcome {
    +winner
    +rewards
}

Experiment --> Simulation
Simulation --> Game
Simulation --> Agent
Simulation --> Outcome
Game --> State
Game --> Action
Agent --> Policy
Policy --> Memory
Agent --> Memory
