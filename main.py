from CTM import CTM
import random

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