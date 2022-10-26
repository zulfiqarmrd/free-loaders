import pandas as pd
import os
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split

import csv
import time
import copy
import chainer
import chainer.functions as F
import chainer.links as L
import numpy as np
from chainer import serializers

class RLScheduler:

    def __init__(self, executers):
        self.executers = executers

        class Q_Network(chainer.Chain):

            def __init__(self, input_size, hidden_size, output_size):
                super(Q_Network, self).__init__(
                    fc1=L.Linear(input_size, hidden_size),
                    fc2=L.Linear(hidden_size, hidden_size),
                    fc3=L.Linear(hidden_size, hidden_size),
                    fc4=L.Linear(hidden_size, hidden_size),
                    fc5=L.Linear(hidden_size, output_size)
                )

            def __call__(self, x):
                h = F.relu(self.fc1(x))
                h = F.relu(self.fc2(h))
                h = F.relu(self.fc3(h))
                h = F.relu(self.fc4(h))
                y = self.fc5(h)
                return y

            def reset(self):
                self.zerograds()

        self.total_executor = 10

        #ToDo, update input size
        self.Q = Q_Network(input_size=102, hidden_size=400, output_size=self.total_executor)

        self.Q_ast = copy.deepcopy(self.Q)
        self.optimizer = chainer.optimizers.Adam()
        self.optimizer.setup(self.Q)

        self.epoch_num = 20
        self.memory_size = 800
        self.batch_size = 20
        self.epsilon = 1.0
        self.epsilon_decrease = 1e-3
        self.epsilon_min = 0.1
        self.start_reduce_epsilon = 200
        self.train_freq = 10
        self.update_q_freq = 20
        self.gamma = 0.97
        self.show_log_freq = 5

        self.memory = []
        self.total_step = 0
        self.total_rewards = []
        self.total_losses = []

        self.state_table = {}

    def save_state(self, task, state, act):

        self.state_table[task.offload_id] = [state, act, task.deadline]

    def get_saved_state(self, offload_id):

        state, act, deadline = self.state_table[offload_id]
        del self.state_table[offload_id]

        return state, act, deadline

    def process_state(self, before_state, task):

        state = []

        task_id_vec = [ord(c) for c in str(task.task_id)]

        state.append(task_id_vec)
        state.append(task.deadline)

        for key in before_state:
            key_vec = [ord(c) for c in key]
            state.append(key_vec)

            state.extend(list(before_state[key].values()))

        return state

    def generate_new_state(self, before_state, new_state_of_executor, exec_id):

        new_state = before_state
        new_state[exec_id] = new_state_of_executor

        return new_state

    def generate_reward(self, deadline, exec_time):

        if exec_time > deadline:
            reward = -np.tanh(exec_time/deadline)
        else:
            reward = 1-np.tanh(exec_time/(deadline+exec_time))

        return reward

    # TODO: When to stop? Optional for now
    def done_with_learning(self, reward):

        #if reached plateau return 1, else return 0

        return 0

    def schedule(self, before_state, task):

        pobs = self.process_state(before_state, task)

        # select act
        pact = np.random.randint(self.total_executor)
        if np.random.rand() > self.epsilon:
            pact = self.Q(np.array(pobs, dtype=np.float32).reshape(1, -1))
            pact = np.argmax(pact.data)

        self.save_state(task, before_state, pact)

        return pact


    def task_finished(self, offload_id, exec_time, new_state_of_executor, exec_id):

        pobs, pact, deadline = self.get_saved_state(offload_id)

        obs = self.generate_new_state(pobs, new_state_of_executor, exec_id)
        reward = self.generate_reward(deadline, exec_time)
        done = self.done_with_learning(reward)

        # add memory
        self.memory.append((pobs, pact, reward, obs, done))
        if len(self.memory) > self.memory_size:
            self.memory.pop(0)

        # train or update q
        if len(self.memory) == self.memory_size:

            f = open('result/reward_loss.csv', 'a', newline='')

            total_reward = 0
            total_loss = 0

            for epoch in range(self.epoch_num):

                if self.total_step % self.train_freq == 0:
                    shuffled_memory = np.random.permutation(self.memory)
                    memory_idx = range(len(shuffled_memory))
                    for i in memory_idx[::self.batch_size]:
                        batch = np.array(shuffled_memory[i:i + self.batch_size])

                        b_pobs = np.array(batch[:, 0].tolist(), dtype=np.float32).reshape(self.batch_size, -1)
                        b_pact = np.array(batch[:, 1].tolist(), dtype=np.int32)

                        b_reward = np.array(batch[:, 2].tolist(), dtype=np.int32)
                        b_obs = np.array(batch[:, 3].tolist(), dtype=np.float32).reshape(self.batch_size, -1)
                        b_done = np.array(batch[:, 4].tolist(), dtype=np.bool)
                        q = self.Q(b_pobs)
                        maxq = np.max(self.Q_ast(b_obs).data, axis=1)
                        target = copy.deepcopy(q.data)
                        for j in range(self.batch_size):
                            target[j, b_pact[j]] = b_reward[j] + self.gamma * maxq[j] * (not b_done[j])
                        self.Q.reset()
                        loss = F.mean_squared_error(q, target)
                        total_loss += loss.data
                        loss.backward()
                        self.optimizer.update()

                if self.total_step % self.update_q_freq == 0:
                    self.Q_ast = copy.deepcopy(self.Q)

                # epsilon
                if self.epsilon > self.epsilon_min and self.total_step > self.start_reduce_epsilon:
                    self.epsilon -= self.epsilon_decrease

                # next step
                total_reward += reward
                self.total_step += 1

            self.total_rewards.append(total_reward)
            self.total_losses.append(total_loss)

            if (epoch + 1) % self.show_log_freq == 0:
                log_reward = sum(self.total_rewards[((epoch + 1) - self.show_log_freq):]) / self.show_log_freq
                log_loss = sum(self.total_losses[((epoch + 1) - self.show_log_freq):]) / self.show_log_freq
                print('\t'.join(map(str, [epoch + 1, self.epsilon, self.total_step, log_reward, log_loss])))

            # save Q, total_losses, total_rewards
            writer = csv.writer(f)
            writer.writerow([str(total_reward), str(total_loss)])
            f.close()

            serializers.save_npz('SavedModels/Q.model', self.Q)
