import gym
from gym import spaces
from ctm import *
import numpy as np

class ctmENV(gym.Env):
    def __init__(self):
        # 定义动作空间和状态空间
        self.action_space = spaces.Discrete(4)  # 两个离散动作
        self.observation_space = spaces.Box(low=0, high=1, shape=(3,))  # 三维状态空间
        self.ctm = CTM()

        self.stepNum = None

        # 初始化环境的内部状态
        self.state = self.np_random.uniform(low=0, high=1, size=(3,))

    def reset(self):
        # 重置环境的状态
        self.ctm.initSate()

        self.state = self._get_state()
        self.stepNum = 0


        return self.state

    def step(self, action):
        # 执行动作并返回下一个状态、奖励和是否终止的标志
        assert self.action_space.contains(action), "Invalid action"

        # 根据动作更新状态
        self.ctm.simulationStep(action)
        self.state = self._get_state()
        self.stepNum += 1

        # 计算奖励
        reward = self._calculate_reward()

        # 判断是否终止
        done = self._is_done()

        # 返回下一个状态、奖励和是否终止的标志
        return self.state, reward, done, {}

    def _get_state(self):
        state =np.zeros((3,))
        state[0] = self.ctm.densityList[self.ctm.onRampID - 2]
        state[1] = self.ctm.densityList[self.ctm.onRampID - 1]
        state[2] = self.ctm.densityList[self.ctm.onRampID]
        return state


    def _calculate_reward(self):
        # 根据当前状态计算奖励
        # 这里只是一个示例，你可以根据自己的需求进行定义
        reward = self.ctm.densityList[self.ctm.onRampID] + self.ctm.lengthQueueList[self.ctm.onRampID]
        return reward

    def _is_done(self):
        # 判断是否终止
        # 这里只是一个示例，你可以根据自己的需求进行定义
        return self.stepNum > 100

    def render(self, mode='human'):
        # 可选的渲染函数，用于可视化环境
        pass

# 创建自定义环境实例
if __name__ == "__main__":
    env = ctmENV()
    observation = env.reset()
    print(observation)

    done = False
    while not done:
        action = env.action_space.sample()  # 示例：随机选择动作
        observation, reward, done, _ = env.step(action)
        print(action, observation, reward, done)

# 使用自定义环境进行强化学习
# ...
