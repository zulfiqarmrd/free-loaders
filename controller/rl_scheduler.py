import pandas as pd
import os
from sklearn.utils import shuffle
from sklearn.model_selection import train_test_split

import time
import copy
import chainer
import chainer.functions as F
import chainer.links as L
from plotly import tools
from plotly.graph_objs import *
from plotly.offline import init_notebook_mode, iplot, iplot_mpl
import numpy as np


class RLScheduler:
    def __init__(self, executers):
        self.executers = executers

    def get_state(self, state, task):

        #merge state and task into correct format
        # To Do
        updated_state = state+ task

        return updated_state


    def generate_reward(self, task, exec_time):

        if exec_time < task.deadline:
            # TO_DO
            reward = 1

        else:
            reward = -1

        return reward


    def done_with_learning(self, reward):

        # To Do
        #if reached plateau return 1, else return 0

        return 0

    def execute_task(self, executers_id, task):

        # start_timer
        start_time = time.time()
        new_observation = execute(executers_id, task) # to_do
        end_time = time.time()

        exec_time = end_time - start_time

        reward = self.generate_reward(task, exec_time)

        done = self.done_with_learning(reward)

        return new_observation, reward, done

    def schedule(self, before_state, task):

        class Q_Network(chainer.Chain):

            def __init__(self, input_size, hidden_size, output_size):
                super(Q_Network, self).__init__(
                    fc1=L.Linear(input_size, hidden_size),
                    fc2=L.Linear(hidden_size, hidden_size),
                    fc3=L.Linear(hidden_size, output_size)
                )

            def __call__(self, x):
                h = F.relu(self.fc1(x))
                h = F.relu(self.fc2(h))
                y = self.fc3(h)
                return y

            def reset(self):
                self.zerograds()

        # To_Do
        Q = Q_Network(input_size=12, hidden_size=100, output_size=2)  # 4 features, 2 actions
        Q_ast = copy.deepcopy(Q)
        optimizer = chainer.optimizers.Adam()
        optimizer.setup(Q)

        epoch_num = 20
        memory_size = 800
        batch_size = 20
        epsilon = 1.0
        epsilon_decrease = 1e-3
        epsilon_min = 0.1
        start_reduce_epsilon = 200
        train_freq = 10
        update_q_freq = 20
        gamma = 0.97
        show_log_freq = 5

        memory = []
        total_step = 0
        total_rewards = []
        total_losses = []

        start = time.time()
        for epoch in range(epoch_num):

            pobs = self.get_state(before_state, task)
            done = False
            total_reward = 0
            total_loss = 0

            while not done: #update

                # select act
                pact = np.random.randint(2) # update with executers id
                if np.random.rand() > epsilon:
                    pact = Q(np.array(pobs, dtype=np.float32).reshape(1, -1))
                    pact = np.argmax(pact.data)

                # act
                obs, reward, done = self.execute_task(pact, task)

                # add memory
                memory.append((pobs, pact, reward, obs, done))
                if len(memory) > memory_size:
                    memory.pop(0)

                # train or update q
                if len(memory) == memory_size:
                    if total_step % train_freq == 0:
                        shuffled_memory = np.random.permutation(memory)
                        memory_idx = range(len(shuffled_memory))
                        for i in memory_idx[::batch_size]:
                            batch = np.array(shuffled_memory[i:i + batch_size])

                            b_pobs = np.array(batch[:, 0].tolist(), dtype=np.float32).reshape(batch_size, -1)
                            b_pact = np.array(batch[:, 1].tolist(), dtype=np.int32)

                            b_reward = np.array(batch[:, 2].tolist(), dtype=np.int32)
                            b_obs = np.array(batch[:, 3].tolist(), dtype=np.float32).reshape(batch_size, -1)
                            b_done = np.array(batch[:, 4].tolist(), dtype=np.bool)
                            q = Q(b_pobs)
                            maxq = np.max(Q_ast(b_obs).data, axis=1)
                            target = copy.deepcopy(q.data)
                            for j in range(batch_size):
                                target[j, b_pact[j]] = b_reward[j] + gamma * maxq[j] * (not b_done[j])
                            Q.reset()
                            loss = F.mean_squared_error(q, target)
                            total_loss += loss.data
                            loss.backward()
                            optimizer.update()

                    if total_step % update_q_freq == 0:
                        Q_ast = copy.deepcopy(Q)

                # epsilon
                if epsilon > epsilon_min and total_step > start_reduce_epsilon:
                    epsilon -= epsilon_decrease

                # next step
                total_reward += reward
                pobs = obs
                total_step += 1

            total_rewards.append(total_reward)
            total_losses.append(total_loss)

        #     if (epoch + 1) % show_log_freq == 0:
        #         log_reward = sum(total_rewards[((epoch + 1) - show_log_freq):]) / show_log_freq
        #         log_loss = sum(total_losses[((epoch + 1) - show_log_freq):]) / show_log_freq
        #         elapsed_time = time.time() - start
        #         print('\t'.join(map(str, [epoch + 1, epsilon, total_step, log_reward, log_loss, elapsed_time])))
        #         start = time.time()
        #
        # return Q, total_losses, total_rewards


        return 0


