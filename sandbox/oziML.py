import numpy as np
import sys
import matplotlib.pyplot as plt

def loadData(filename):
    my_arr=[]
    with open(filename) as textFile:
        my_arr=[line.rstrip().split(',') for line in textFile]
    return my_arr

def computeCost(X,y,theta):
    m=np.size(X,0)
    predictions=np.array(np.dot(X,theta))
    sqrErrors=np.square(np.subtract(predictions,y))
    J=np.sum(sqrErrors)/(2*m)
    return J

def seperateXy(data):
    m=np.size(data,0)
    onesArr=np.ones((m,1))
    x=np.array(data[:,[0]]).astype(float)
    X=np.array(np.concatenate((onesArr,x),axis=1))
    y=np.array(data[:,[1]]).astype(float)

    return X,y

def plotData(X,y,xlbl,ylbl,plotshow,plottype):
    plt.plot(X,y,plottype)
    plt.xlabel(xlbl)
    plt.ylabel(ylbl)
    if plotshow == True:
        plt.show()

def gradientDescent(X, y, theta, alpha, num_iters):
    m=np.size(X,0)
    J_History=np.zeros((num_iters,1))
    for i in range(num_iters):
        x=np.array(X[:,[1]])
        h=theta[0]+np.multiply(np.array([theta[1]]),x)
        theta[0]=theta[0]-(alpha * (1/m) * np.sum( np.subtract(h,y) ) )
        theta[1]=theta[1]-(alpha * (1/m) * np.sum( np.multiply( np.subtract(h,y) , x ) ) )
        J_History[i] = computeCost(X, y, theta)
    return theta,J_History

def main(argv):
    data=np.array(loadData("ex1data1.txt"))
    [X,y]=seperateXy(data)
    plotData(X[:,[1]],y,"Label X","Label Y",False,"ro")
    theta=np.zeros((2,1))
    [theta,jhistory]=gradientDescent(X,y,theta,0.01,1500)
    plotData(X[:,[1]],X.dot(theta),"Label X","Label Y",True,"")

if __name__ == "__main__":
    main(sys.argv[1:])
