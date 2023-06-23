import pandas as pd
import matplotlib.pyplot as plt
import random
import seaborn as sns


class CTM(object):
    
    def __init__(self):
        
        #PARAMETERS
        self.numberCell = 11 #num        
        self.deltaLength = 0.5 #km
        self.deltaTime = 1/180 #h ==20s 1min~3
        self.speedWave = 35 #km/h
        self.flowMax = 8000 #veh/h
        self.densityMax = 450 #veh/km
        
        #INPUTS    
        self.demandOnRampList = [0] * self.numberCell #veh/h        
        self.demandZero = 6000 #veh/h        
        self.flowOffRampList = [0] * self.numberCell #veh/h   

        #STATES
        self.densityList = [80] * (self.numberCell + 1) #veh/km
        self.flowExitList = [0] * self.numberCell #veh/h
        self.flowEnterList = [0] * self.numberCell #veh/h
        self.flowOnRampList = [0] * self.numberCell #veh/h
        self.lengthQueueList = [0] * self.numberCell #veh
        
        #CONTROL        
        self.speedFreeList = [100] * (self.numberCell + 1) #km/h
        self.RatioOnRampList = [1] * self.numberCell
        
        #DATA
        self.densityDF = pd.DataFrame(columns=[list(range(0, self.numberCell+1))])
        self.flowExitDF = pd.DataFrame(columns=[list(range(1, self.numberCell+1))])
        self.flowEnterDF = pd.DataFrame(columns=[list(range(1, self.numberCell+1))])
        self.lengthQueueDF = pd.DataFrame(columns=[list(range(1, self.numberCell+1))])
        self.flowOnRampDF = pd.DataFrame(columns=[list(range(1, self.numberCell+1))])
        # self.densityDF = pd.DataFrame(columns=['0','1','2','3','4','5','6','7','8','9','10'])
        # self.flowExitDF = pd.DataFrame(columns=['1','2','3','4','5','6','7','8','9','10'])
        # self.flowEnterDF = pd.DataFrame(columns=['1','2','3','4','5','6','7','8','9','10'])
        # self.lengthQueueDF = pd.DataFrame(columns=['1','2','3','4','5','6','7','8','9','10'])
        # self.flowOnRampDF = pd.DataFrame(columns=['1','2','3','4','5','6','7','8','9','10'])


        
        
    def start(self):
        
        print('Let go')
        
    
    def simulationStep(self):
        
        for i in range(self.numberCell):
            self.flowOnRampList[i] = self.calFlowRamp(i)
            self.flowEnterList[i] = self.calFlowEnter(i)
            self.flowExitList[i] = self.calFlowExit(i)
            
        for  i in range(self.numberCell):
            self.lengthQueueList[i] = self.calQueueLength(i)
        
        # i=0
        i = 0
        self.densityList[i] = self.calDensity(i, self.demandZero)
        # i>0
        for i in range(self.numberCell-1):
            self.densityList[i+1] = self.calDensity(i, self.flowEnterList[i])
            
        self.saveData()
            
    def saveData(self):
        
        self.densityDF.loc[self.densityDF.shape[0]] = self.densityList    
        self.flowExitDF.loc[self.flowExitDF.shape[0]] = self.flowExitList
        self.flowEnterDF.loc[self.flowEnterDF.shape[0]] = self.flowEnterList
        self.lengthQueueDF.loc[self.lengthQueueDF.shape[0]] = self.lengthQueueList
        self.flowOnRampDF.loc[self.flowOnRampDF.shape[0]] = self.flowOnRampList
        
        
        
    def close(self):
        print('finish')
        
    
    def show(self):
        
        plt.figure()
        plot = sns.heatmap(self.densityDF)
        plt.title('density of each segment')

        # plt.figure()
        # plot = sns.heatmap(self.flowExitDF)
        # plt.title('flow of each segment exit')

        # plt.figure()
        # plot = sns.heatmap(self.flowEnterDF)
        # plt.title('flow of each segment enter')

        # plt.figure()
        # plot = sns.heatmap(self.flowOnRampDF)
        # plt.title('flow of each onramp')

        plt.figure()
        plot = sns.heatmap(self.lengthQueueDF)
        plt.title('length of each onramp')
        
        plt.show()
          
        
    def calFlowRamp(self, i):
        
        value_1 = self.lengthQueueList[i] / self.deltaTime
        value_2 = min(self.flowMax - self.speedFreeList[i] * self.densityList[i], self.speedWave * (self.densityMax - self.densityList[i+1]))
        
        return self.RatioOnRampList[i]*min(value_1, value_2)


    def calFlowEnter(self, i):
        
        value_1 = self.speedFreeList[i] * self.densityList[i] + self.flowOnRampList[i] - self.flowOffRampList[i]
        value_2 = self.speedWave * (self.densityMax - self.densityList[i+1])
        
        return min(value_1, value_2)


    def calFlowExit(self, i):
        
        value = self.flowEnterList[i] - self.flowOnRampList[i] + self.flowOffRampList[i]
        
        return value


    def calQueueLength(self, i):
        
        value = self.lengthQueueList[i] + self.deltaTime * (self.demandOnRampList[i] - self.flowOnRampList[i])
        
        return value


    def calDensity(self, i, flowEnter):
        
        value = self.densityList[i+1] + self.deltaTime * (flowEnter - self.flowExitList[i+1]) / self.deltaLength
        
        return value
    
    
    def changeDemandZero(self, changeValue):
        
        self.demandZero = changeValue           
        
        
    def changeDemandOnRamp(self, changeValue, id):
        
        self.demandOnRampList[id-1] = changeValue     
        
        
    def changeFlowOffRamp(self, changeValue, id):
        
        self.flowOffRampList[id-1] = changeValue
        
    
    def changeSpeedFree(self, changeValue, id):
        
        self.speedFreeList[id] = changeValue   
        
    
    def changeRatioOnRamp(self, changeValue, id):
        
        self.RatioOnRampList[id-1] = changeValue


            

if __name__ == '__main__':
    
    ctm = CTM()
    
    ctm.start()
    
    idOnRamp = 7
    
    step = 0    
    while step < 360:        
        ctm.simulationStep()
        
        if step % 15 == 0 :        
            ctm.changeDemandZero(5000 + random.randint(-500, 500))
            ctm.changeDemandOnRamp(2000 + random.randint(-500, 500), idOnRamp)
              
        if step % 15 == 0 :            
            ctm.changeRatioOnRamp(random.choice([0.6, 0.7, 0.8, 0.9, 1]), idOnRamp)
        
        # ctm.saveData()
        step = step + 1
        
    ctm.close()
    
    ctm.show()
    
    
    
        

    

        
