# MDP Value Iteration and Policy Iteration
import argparse
import numpy as np
import gymnasium as gym
import time
from lake_envs import *
from gymnasium.envs.toy_text.frozen_lake import generate_random_map

np.set_printoptions(precision=3)

parser = argparse.ArgumentParser(
    description="A program to run assignment 1 implementations.",
    formatter_class=argparse.ArgumentDefaultsHelpFormatter,
)

parser.add_argument(
    "--env",
    type=str,
    help="The name of the environment to run your algorithm on.",
    choices=["Deterministic-4x4-FrozenLake-v0", "FrozenLake8x8"],
    default="FrozenLake8x8",
)

parser.add_argument(
    "--render-mode",
    "-r",
    type=str,
    help="The render mode for the environment. 'human' opens a window to render. 'ansi' does not render anything.",
    choices=["human", "ansi"],
    default="human",
)

"""
For policy_evaluation, policy_improvement, policy_iteration and value_iteration,
the parameters P, nS, nA, gamma are defined as follows:

	P: nested dictionary of a nested lists
		From gym.core.Environment
		For each pair of states in [1, nS] and actions in [1, nA], P[state][action] is a
		tuple of the form (probability, nextstate, reward, terminal) where
			- probability: float
				the probability of transitioning from "state" to "nextstate" with "action"
			- nextstate: int
				denotes the state we transition to (in range [0, nS - 1])
			- reward: int
				either 0 or 1, the reward for transitioning from "state" to
				"nextstate" with "action"
			- terminal: bool
			  True when "nextstate" is a terminal state (hole or goal), False otherwise
	nS: int
		number of states in the environment
	nA: int
		number of actions in the environment
	gamma: float
		Discount factor. Number in range [0, 1)
"""


def policy_evaluation(P, nS, nA, policy, gamma=0.9, tol=1e-3):
    """Evaluate the value function from a given policy.

        Parameters
        ----------
        P, nS, nA, gamma:
                defined at beginning of file
        policy: np.array[nS]
                The policy to evaluate. Maps states to actions.
        tol: float
                Terminate policy evaluation when
                        max |value_function(s) - prev_value_function(s)| < tol
        Returns
        -------
        value_function: np.ndarray[nS]
                The value function of the given policy, where value_function[s] is
                the value of state s
        """

    value_function = np.zeros(nS)
    max_change = tol+1
    ############################
    while max_change > tol:

        value_function_new = np.copy(value_function)
        for s in range(nS):
            t_action = policy[s]

            listt = P[s][t_action]
            total = 0
            for i in listt:
                prob, next_state, reward, terminal = i
                total += prob*(reward + (value_function[next_state]*gamma))

            value_function_new[s] = total

        max_change = np.max(np.abs(value_function_new-value_function))

        value_function = np.copy(value_function_new)

        if max_change <= tol:
            break

    ############################
    return value_function


def policy_improvement(P, nS, nA, value_from_policy, policy, gamma=0.9):
    """Given the value function from policy improve the policy.

        Parameters
        ----------
        P, nS, nA, gamma:
                defined at beginning of file
        value_from_policy: np.ndarray
                The value calculated from the policy
        policy: np.array
                The previous policy.

        Returns
        -------
        new_policy: np.ndarray[nS]
                An array of integers. Each integer is the optimal action to take
                in that state according to the environment dynamics and the
                given value function.
        """
    new_policy = np.zeros(nS, dtype="int")

    ############################
    Q = np.zeros((nS, nA))

    for s in range(nS):

        for a in range(nA):
            listt = P[s][a]
            total = 0
            for i in listt:
                prob, next_state, reward, terminal = i
                total += prob*(reward+(gamma * value_from_policy[next_state]))

            Q[s][a] = total

    new_policy = np.argmax(Q, axis=1)

    ############################
    return new_policy


def policy_iteration(P, nS, nA, gamma=0.9, tol=1e-3):
    """Runs policy iteration.

        You should call the policy_evaluation() and policy_improvement() methods to
        implement this method.

        Parameters
        ----------
        P, nS, nA, gamma:
                defined at beginning of file
        tol: float
                tol parameter used in policy_evaluation()
        Returns:
        ----------
        value_function: np.ndarray[nS]
        policy: np.ndarray[nS]
        """

    value_function = np.zeros(nS)
    policy = np.zeros(nS, dtype=int)

    ############################
    while True:

        value_function_new = policy_evaluation(P, nS, nA, policy, gamma, tol)
        new_policy = policy_improvement(
            P, nS, nA, value_function_new, policy, gamma)
        if np.array_equal(policy, new_policy):
            break
        policy = np.copy(new_policy)
        value_function = np.copy(value_function_new)
    ############################
    return value_function, policy


def value_iteration(P, nS, nA, gamma=0.9, tol=1e-3):
    """
        Learn value function and policy by using value iteration method for a given
        gamma and environment.

        Parameters:
        ----------
        P, nS, nA, gamma:
                defined at beginning of file
        tol: float
                Terminate value iteration when
                        max |value_function(s) - prev_value_function(s)| < tol
        Returns:
        ----------
        value_function: np.ndarray[nS]
        policy: np.ndarray[nS]
        """

    value_function = np.zeros(nS)
    policy = np.zeros(nS, dtype=int)
    ############################

    while True:
        value_function_new = np.copy(value_function)
        for s in range(nS):
            Q = np.zeros(nA)
            for a in range(nA):
                listt = P[s][a]
                total = 0
                for i in listt:
                    prob, next_state, reward, terminal = i
                    total += prob*(reward+(gamma * value_function[next_state]))
                Q[a] = total
            value_function_new[s] = np.max(Q)
            policy[s] = np.argmax(Q)

        if np.max(np.abs(value_function_new-value_function)) <= tol:
            break

        value_function = np.copy(value_function_new)

    ############################
    return value_function, policy


def render_single(env, policy, max_steps=100):
    """
    This function does not need to be modified
    Renders policy once on environment. Watch your agent play!

    Parameters
    ----------
    env: gym.core.Environment
      Environment to play on. Must have nS, nA, and P as
      attributes.
    Policy: np.array of shape [env.nS]
      The action to take at a given state
  """

    episode_reward = 0
    ob, _ = env.reset()
    for t in range(max_steps):
        env.render()
        time.sleep(0.25)
        a = policy[ob]
        ob, rew, done, _, _ = env.step(a)
        episode_reward += rew
        if done:
            break
    env.render()
    if not done:
        print(
            "The agent didn't reach a terminal state in {} steps.".format(
                max_steps
            )
        )
    else:
        print("Episode reward: %f" % episode_reward)


# Edit below to run policy and value iteration on different environments and
# visualize the resulting policies in action!
# You may change the parameters in the functions below
if __name__ == "__main__":
    # read in script argument
    args = parser.parse_args()

    # Make gym environment
    size = int(input("Enter the size of the map: "))
    probability = float(input("Enter the probability of in the map: "))

    slippy = input("Do you want the map to be slippery? (y/n): ")
    if slippy == 'y':
        slippy = True
    else:
        slippy = False

    desc = generate_random_map(size=size, p=1-probability)
    env = gym.make(args.env, render_mode=args.render_mode,
                   is_slippery=slippy, desc=desc)

    env.nS = env.nrow * env.ncol
    env.nA = 4

    print("\n" + "-" * 25 + "\nBeginning Policy Iteration\n" + "-" * 25)

    V_pi, p_pi = policy_iteration(env.P, env.nS, env.nA, gamma=0.9, tol=1e-3)
    render_single(env, p_pi, 100)

    print("\n" + "-" * 25 + "\nBeginning Value Iteration\n" + "-" * 25)

    V_vi, p_vi = value_iteration(env.P, env.nS, env.nA, gamma=0.9, tol=1e-3)
    render_single(env, p_vi, 100)
