import numpy as np

# bezier parameter
def getBezParam(t):
    param = np.zeros([1, 4])
    param[0][0] = -t*t*t+3*t*t-3*t+1
    param[0][1] = 3*t*t*t-6*t*t+3*t
    param[0][2] = -3*t*t*t+3*t*t
    param[0][3] = t*t*t
    return param

def leastsq(pts):
    ptSize = len(pts)
    # turn pt to pt matrix
    ptMat = np.zeros([ptSize, 3])
    for i,pt in enumerate(pts):
        ptMat[i] = pt
    # calculate bezier parameter matrix
    bezMat = np.zeros([ptSize, 4])
    for i in range(ptSize):
        t = i / (ptSize - 1)
        bezMat[i] = getBezParam(t)
    bezMatTras = bezMat.transpose()
    # calculate inverse matrix
    try:
        inverse = np.linalg.inv(bezMatTras.dot(bezMat))
    except np.linalg.LinAlgError:
        print("Inverse Error")
        return
    answer = inverse.dot(bezMatTras.dot(ptMat))
    print(answer)
    return answer
    
size = 10
array = [None] * size

for i in range(size):
    array[i] = np.array([i,0,0])
array[5][1] = 1 
print(array)
leastsq(array)