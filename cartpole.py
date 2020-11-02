import tensorflow as tf
import numpy as np
from tensorflow.keras import Model
import tensorflow_probability as tfp
import gym
import matplotlib.pyplot as plt

class MakeModel(Model):
    def __init__(self,num_actions):
        super().__init__()
        self.fc1 = tf.keras.layers.Dense(64,activation='relu')
        self.fc2 = tf.keras.layers.Dense(64,activation='relu')
        self.action = tf.keras.layers.Dense(num_actions,activation='softmax')
        

    def call(self,state):
        x = tf.convert_to_tensor(state)
        x = self.fc1(x)
        x = self.fc2(x)
        x = self.action(x)
        return x

class Agent:
    def __init__(self,gamma=0.95,lr=0.001,n_actions=2):
        self.gamma = gamma
        self.lr = lr
        self.model = MakeModel(n_actions)
        self.opt = tf.keras.optimizers.Adam(learning_rate=self.lr)
        self.action_memory = []
        self.reward_memory = []
        self.state_memory = []

    def choose_action(self,state):
        prob = self.model(np.array([state]))
        dist = tfp.distributions.Categorical(probs=prob,dtype=tf.float32)
        action = dist.sample()
        self.action_memory.append(action)
        return int(action.numpy()[0])

    def store_reward(self,reward):
        self.reward_memory.append(reward)

    def store_state(self,state):
        self.state_memory.append(state)

    def learn(self):
        sum_reward = 0
        discnt_rewards = []
        self.reward_memory.reverse()
        for r in self.reward_memory:
            sum_reward = r + self.gamma*sum_reward
            discnt_rewards.append(sum_reward)
        discnt_rewards.reverse() 
        

        for state,action,reward in zip(self.state_memory,self.action_memory,discnt_rewards):
            with tf.GradientTape() as tape:
                p = self.model(np.array([state]),training=True)
                loss = self.calc_loss(p,action,reward)
                grads = tape.gradient(loss,self.model.trainable_variables)
                self.opt.apply_gradients(zip(grads,self.model.trainable_variables))

        self.reward_memory = []
        self.action_memory = []
        self.state_memory = []

    def calc_loss(self,prob,action,reward):
        dist = tfp.distributions.Categorical(probs=prob, dtype=tf.float32)
        log_prob = dist.log_prob(action)
        loss = -log_prob*reward
        return loss 


## Training

env = gym.make('CartPole-v0')
agent = Agent()
num_episodes = 10000
total_rewards = []
for i in range(num_episodes):
    state = env.reset()
    score = 0
    rewards = []
    states = []
    actions = []
    done = False
    while not done:
        action = agent.choose_action(state)
        state_,reward,done,_ = env.step(action)
        agent.store_reward(reward)
        agent.store_state(state)
        state = state_
        score += reward
        # env.render()
        if done:
            agent.learn()
            print(f'episode: {i+1}\t reward: {score}')
            total_rewards.append(score)

plt.figure(figsize=(15,8))
plt.plot(total_rewards/num_episodes)
plt.title('Rewards in epochs')
plt.xlabel('epochs'), plt.ylabel('rewards (length)')
plt.show()
plt.savefig('Cartpole_plot.png')
