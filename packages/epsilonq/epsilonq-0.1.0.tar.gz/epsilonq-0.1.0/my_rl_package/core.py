import random

def epsilon_greedy(q_values, epsilon):
    """Select an action using epsilon-greedy strategy."""
    if random.random() < epsilon:
        return random.randint(0, len(q_values) - 1)
    return q_values.index(max(q_values))

def q_learning_update(Q, state, action, reward, next_state, alpha, gamma):
    """Perform the Q-learning update step."""
    if state not in Q:
        Q[state] = [0.0] * (action + 1)
    if next_state not in Q:
        Q[next_state] = [0.0] * len(Q[state])

    max_next_q = max(Q[next_state]) if Q[next_state] else 0.0
    Q[state][action] += alpha * (reward + gamma * max_next_q - Q[state][action])
