import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from statistics import median


# 20230925
# 根据《Design of networked freeway traffic controllers based on# event-triggered control concepts》进行模型改进


class CTM(object):

    def __init__(self):

        # PARAMETERS
        self.numberCell = 10  # num
        self.offRampID = 5 # 下匝道的序号
        self.onRampID = 7 # 上匝道的序号
        self.deltaLength = 0.5  # km
        self.deltaTime = 1 / 180  # h == 20s 1min~3
        self.speedWave = 35  # km/h 反传播速度
        self.flowMax = 8000  # veh/h
        self.flowMaxList = [self.flowMax] * self.numberCell
        self.densityMax = 450  # veh/km
        self.densityOriginal = 80  # 初始化密度
        self.speedFree = 100
        self.speedFreeList = [self.speedFree] * self.numberCell  # km/h
        self.betaList = [0] * self.numberCell  # offRamp split ratio
        self.betaList[self.offRampID] = 0.05
        self.priorityList = [0] * self.numberCell  # priority of the on-ramp flow with respect to the mainstream flow
        self.priorityList[self.onRampID] = 0.4
        self.flowOnRampMax = 2000 # 匝道的最大流量
        self.flowOnRampMaxList = [0] * self.numberCell
        self.flowOnRampMaxList[self.onRampID] = self.flowOnRampMax

        # INPUTS
        self.demandZero = 6000  # veh/h
        self.demandOnRampList = [0] * self.numberCell  # veh/h
        self.demandOnRampList[self.onRampID] = 1500

        # STATES
        self.densityList = [self.densityOriginal] * self.numberCell  # veh/km
        self.flowList = [0] * (self.numberCell + 1)
        self.flowExitList = [0] * self.numberCell  # veh/h
        self.flowEnterList = [0] * self.numberCell  # veh/h
        self.flowOnRampList = [0] * self.numberCell  # veh/h
        self.flowOffRampList = [0] * self.numberCell  # veh/h
        self.lengthQueueList = [0] * self.numberCell  # veh

        # CONTROL
        self.flowOnRampControlList = [0] * self.numberCell
        self.flowOnRampControlList[self.onRampID] = self.flowOnRampMax

        # # DATA
        # self.densityDF = pd.DataFrame(columns=[list(range(self.numberCell))])
        # self.flowDF = pd.DataFrame(columns=[list(range(self.numberCell+1))])
        # self.flowOnRampDF = pd.DataFrame(columns=[list(range(self.numberCell))])
        # self.flowOffRampDF = pd.DataFrame(columns=[list(range(self.numberCell))])
        # self.lengthQueueDF = pd.DataFrame(columns=[list(range(self.numberCell))])

        # 状态转换相关的参数
        self.densityEachLevel = 50
        self.lineEachLevel = 50


    def start(self):
        print('Let go')

    def simulationStep(self, action):

        flowOnRampTempList = [0] * self.numberCell
        flowEnterList = [0] * self.numberCell
        flowExitList = [0] * self.numberCell

        for i in range(self.numberCell):
            # 1 cal flowEnter
            flowEnterList[i] = self.calFlowEntry(i)
            # 2 cal flowExit
            flowExitList[i] = self.calFlowExit(i)
            # 3 cal flowOnRampTemp
            flowOnRampTempList[i] = self.calFlowOnRampTemp(i)

        # demandList 插入一个元素
        flowExitList.insert(0, self.demandZero)
        # 计算流量
        for i in range(self.numberCell):
            # 4 compare relationship, and determine
            if flowExitList[i] + flowOnRampTempList[i] <= flowEnterList[i]:
                self.flowList[i] = flowExitList[i]
                self.flowOnRampList[i] = flowOnRampTempList[i]
            else:
                self.flowList[i] = median([flowExitList[i], flowEnterList[i] - flowOnRampTempList[i], (1 - self.priorityList[i]) * flowEnterList[i]])
                self.flowOnRampList[i] = median([flowOnRampTempList[i], flowEnterList[i] - flowExitList[i], self.priorityList[i] * flowEnterList[i]])

        self.flowList[self.numberCell] = flowExitList[self.numberCell]

        # 计算密度和排队长度
        for i in range(self.numberCell):
            self.densityList[i] = self.calDensity(i)
            self.lengthQueueList[i] = self.calQueueLength(i)



    def saveData(self):
        self.densityDF.loc[self.densityDF.shape[0]] = self.densityList
        self.lengthQueueDF.loc[self.lengthQueueDF.shape[0]] = self.lengthQueueList
        self.flowOnRampDF.loc[self.flowOnRampDF.shape[0]] = self.flowOnRampList
        self.flowDF.loc[self.flowDF.shape[0]] = self.flowList

    def close(self):
        print('finish')

    def show(self):
        plt.figure()
        plot = sns.heatmap(self.densityDF)
        plt.title('density of each segment')
        plt.figure()
        plot = sns.heatmap(self.flowDF)
        plt.title('flow of each segment')
        plt.figure()
        plot = sns.heatmap(self.flowOnRampDF)
        plt.title('flow of each onramp')
        plt.figure()
        plot = sns.heatmap(self.lengthQueueDF)
        plt.title('length of each onramp')
        plt.show()

    def calFlowExit(self, i):
        value = (1 - self.betaList[i]) * self.speedFreeList[i] * self.densityList[i]
        return min(value, self.flowMaxList[i])

    def calFlowEntry(self, i):
        value = self.speedWave * (self.densityMax - self.densityList[i])
        return min(value, self.flowMaxList[i])

    def calFlowOnRampTemp(self, i):
        value = self.demandOnRampList[i] + self.lengthQueueList[i]/self.deltaTime
        valueCap = self.flowOnRampMaxList[i]
        valueControl = self.flowOnRampControlList[i]
        return min(value, valueCap, valueControl)

    def calDensity(self, i):
        parameterOffRamp = self.betaList[i] / (1 - self.betaList[i])
        value = self.densityList[i] + self.deltaTime * (self.flowList[i] + self.flowOnRampList[i] - (1 + parameterOffRamp) * self.flowList[i+1]) / self.deltaLength
        return value

    def calQueueLength(self, i):
        value = self.lengthQueueList[i] + self.deltaTime * (self.demandOnRampList[i] - self.flowOnRampList[i])
        return value

    def setDemandZero(self, changeValue):
        self.demandZero = changeValue

    def setDemandOnRamp(self, changeValue):
        self.demandOnRampList[self.onRampID] = changeValue

    def setSpeedFree(self, changeValue, id):
        self.speedFreeList[id] = changeValue

    def setFlowOnRampControl(self, changeValue):
        self.flowOnRampControlList[self.onRampID] = changeValue

    def calTotalTravelTime(self):
        ttt = self.deltaTime * self.deltaLength * (self.densityList[self.onRampID-1] + self.densityList[self.onRampID-2])
        return ttt

    def calTotalWaitingTime(self):
        twt = self.deltaTime * sum(self.lengthQueueList)
        return twt

    def density2state(self, density):
        state = int(density/self.densityEachLevel)
        return state

    def line2state(self, lineLength):
        state = int(lineLength/self.lineEachLevel)
        if state > 4:
            state = 4
        return state

    def initSate(self):
        # STATES
        self.densityList = [self.densityOriginal] * self.numberCell  # veh/km
        self.flowList = [0] * (self.numberCell + 1)
        self.flowExitList = [0] * self.numberCell  # veh/h
        self.flowEnterList = [0] * self.numberCell  # veh/h
        self.flowOnRampList = [0] * self.numberCell  # veh/h
        self.flowOffRampList = [0] * self.numberCell  # veh/h
        self.lengthQueueList = [0] * self.numberCell  # veh

