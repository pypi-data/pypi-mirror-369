import random
from collections import deque, namedtuple

class ReplayBuffer:
    def __init__(self, capacity):
        self.buffer = deque(maxlen=capacity)
        self.experience = namedtuple("Experience", 
                                     ["state", "action", "reward", "next_state", "done"])

    def push(self, state, action, reward, next_state, done):
        self.buffer.append(self.experience(state, action, reward, next_state, done))

    def sample(self, batch_size):
        return random.sample(self.buffer, batch_size)

    def __len__(self):
        return len(self.buffer)
