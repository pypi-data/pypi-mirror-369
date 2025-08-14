import gym
from .agent import DQNAgent

def train_dqn(episodes=500, batch_size=64, target_update=10):
    env = gym.make("CartPole-v1")
    agent = DQNAgent(env.observation_space.shape[0], env.action_space.n)

    for episode in range(episodes):
        state = env.reset()[0]
        total_reward = 0
        done = False
        while not done:
            action = agent.act(state)
            next_state, reward, done, _, _ = env.step(action)
            agent.remember(state, action, reward, next_state, done)
            agent.replay(batch_size)
            state = next_state
            total_reward += reward

        if episode % target_update == 0:
            agent.update_target()
        print(f"Episode {episode} - Total Reward: {total_reward}")

    env.close()
