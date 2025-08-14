import gymnasium as gym
import numpy as np

network_nodes_definition = {
    # Startknoten (speziell, nicht Teil der Haupt-Traversierungs-Map)
    "S": {"type": "S", "next_node_id": 2},

    # J-Knoten für obs[3] (Pol-Winkelgeschwindigkeit)
    # Original: J id: 0 F: 3 edges (2): 4 2 boundaries(3): -10 0.0551312 10
    # Interpretation: Binäre Entscheidung, ein Schwellenwert (0.0551312)
    0: {"type": "J", "feature_idx": 3, "branches": [4, 2], "thresholds": [0.0551312]},

    # P-Knoten, Aktion 0
    # Original: P id: 1 F: 0 k: 0 d: 0 edges (1): 0
    # Interpretation: Gibt Aktion 0 zurück. 'edges' wird für eine zustandslose Policy ignoriert.
    1: {"type": "P", "action_value": 0, "branches": [0]},

    # P-Knoten, Aktion 1
    # Original: P id: 2 F: 1 k: 0 d: 0 edges (1): 4
    # Interpretation: Gibt Aktion 1 zurück. 'edges' wird für eine zustandslose Policy ignoriert.
    2: {"type": "P", "action_value": 1, "branches": [4]},

    # P-Knoten, Aktion 0
    # Original: P id: 3 F: 0 k: 0 d: 0 edges (1): 5
    # Interpretation: Gibt Aktion 0 zurück. 'edges' wird für eine zustandslose Policy ignoriert.
    3: {"type": "P", "action_value": 0, "branches":[5]},

    # J-Knoten für obs[2] (Pol-Winkel)
    # Original: J id: 4 F: 2 edges (2): 1 2 boundaries(3): -0.418 0.0152164 0.418
    # Interpretation: Binäre Entscheidung, ein Schwellenwert (0.0152164)
    4: {"type": "J", "feature_idx": 2, "branches": [1, 2], "thresholds": [0.0152164]},

    # J-Knoten für obs[2] (Pol-Winkel)
    # Original: J id: 5 F: 2 edges (3): 0 2 0 boundaries(4): -0.418 -0.165754 0.149135 0.418
    # Interpretation: Ternäre Entscheidung, zwei Schwellenwerte (-0.165754, 0.149135)
    5: {"type": "J", "feature_idx": 2, "branches": [0, 2, 0], "thresholds": [-0.165754, 0.149135]}
}

# Die Policy-Funktion, die eine Beobachtung entgegennimmt und das Netzwerk durchläuft
def network_policy(observation: np.ndarray, current_node_id = 0):
    """
    Durchläuft das definierte Netzwerk, um eine Aktion basierend auf der Beobachtung zu bestimmen.

    Args:
        observation (np.ndarray): Der aktuelle Zustand der Umgebung ([x, x_dot, theta, theta_dot]).
        nodes_map (dict): Die Definition aller Knoten im Netzwerk.

    Returns:
        int: Die zu ergreifende Aktion (0 für links, 1 für rechts).
    """
    while True:
        node = network_nodes_definition[current_node_id] 
        if node["type"] == "P":
            return (node["action_value"], node["branches"][0])
        elif node["type"] == "J":
            feature_value = observation[node["feature_idx"]]
            thresholds = node["thresholds"]
            branches = node["branches"]
            
            selected_branch_idx = 0
            for i, threshold in enumerate(thresholds):
                if feature_value > threshold:
                    selected_branch_idx = i + 1
                else:
                    break # Das richtige Intervall wurde gefunden
            
            # Sicherstellen, dass der ausgewählte Zweig-Index innerhalb der Grenzen der branches-Liste liegt
            if selected_branch_idx >= len(branches):
                # Dies sollte bei korrekten Schwellenwerten nicht passieren.
                # Fallback zum letzten Zweig, falls außerhalb der Grenzen.
                print(f"Warnung: Policy-Zweig-Index außerhalb der Grenzen für Knoten {current_node_id}. Standard auf ersten Zweig.")
                selected_branch_idx = 0 # Oder len(branches) - 1, je nach gewünschtem Fallback

            current_node_id = branches[selected_branch_idx]
        else:
            # Sollte bei gültigen Knotentypen nicht vorkommen
            raise ValueError(f"Unbekannter Knotentyp: {node['type']} für Knoten-ID {current_node_id}")


# Entscheidungsbaum-Policy gemäß DTPO-Baum aus dem Bild
def dtpo_policy(observation):
    # observation = [cart_pos, cart_vel, pole_angle, pole_ang_velocity]
    pole_angle = observation[2]
    pole_ang_vel = observation[3]

    if pole_ang_vel <= 0.021:
        if pole_angle <= 0.017:
            return 0  # left
        else:
            return 1  # right
    else:
        if pole_angle <= -0.043:
            return 0  # left
        else:
            return 1  # right

# Testumgebung: CartPole-v1 (max. 500 Schritte)
env = gym.make("CartPole-v1", render_mode=None)

n_episodes = 1000
episode_lengths = []

for _ in range(n_episodes):
    obs, _ = env.reset()
    done = False
    steps = 0

    currentNode = 2
    while not done:
        #action = dtpo_policy(obs)
        result = network_policy(obs, currentNode)
        action = result[0]
        currentNode = result[1]
        obs, reward, terminated, truncated, _ = env.step(action)
        steps += 1
        done = terminated or truncated

    episode_lengths.append(steps)
    print(f"steps: {steps}")

env.close()

# Ergebnisse anzeigen
mean = np.mean(episode_lengths)
std = np.std(episode_lengths)
print(f"Durchschnittliche Episodenlänge über {n_episodes} Läufe: {mean:.1f} ± {std:.1f}")

