import numpy as np
import matplotlib.pyplot as plt


# 하이퍼 파라미터 정의
n_in = 40
n_mid1 = 128
n_mid2 = 64
n_out = 2
wb_width = 0.1
eta = 0.01
epoch = 500
batch_size = 25
interval = 10
stock_data_interval = 5
n_stock_data = 400
num_for_one_stock = 20
def stable_softmax(u):
    # 입력값 u의 각 행에서 최대값을 뺍니다.
    max_u = np.max(u, axis=1, keepdims=True)
    exp_u = np.exp(u - max_u)  # 오버플로우 방지
    softmax_output = exp_u / np.sum(exp_u, axis=1, keepdims=True)
    return softmax_output

# 각 층의 부모 클래스 생성
class BaseLayer:
    def __init__(self, n_upper, n):

        #self.w = wb_width * np.random.randn(n_upper, n)
        #self.b = wb_width * np.random.randn(n)

        # 아다그리드

        self.w = wb_width * np.random.randn(n_upper, n)
        self.b = wb_width * np.random.randn(n)
        self.h_w = np.zeros((n_upper, n)) + 1e-8
        self.h_b = np.zeros(n) + 1e-8

    def update(self, eta):
        #self.w -= eta * self.grad_w
        #self.b -= eta * self.grad_b

        # 아다그리드

        self.h_w += self.grad_w * self.grad_w
        self.w -= eta / np.sqrt(self.h_w)*self.grad_w

        self.h_b += self.grad_b * self.grad_b
        self.b -= eta / np.sqrt(self.h_b)*self.grad_b

    def getW(self):
        return self.w

    def getB(self):
        return self.b
    def putW(self, w):
        self.w = np.array(w, dtype=float)
    def putB(self, b):
        self.b = np.array(b, dtype=float)



class MiddleLayer(BaseLayer):
    def forward(self, x):
        self.x = x
        self.u = np.dot(x, self.w) + self.b
        self.y = np.where(self.u <=0,0, self.u)

    def backward(self, grad_y):
        delta = grad_y * np.where(self.u<=0,0,1)

        self.grad_w = np.dot(self.x.T, delta)
        self.grad_b = np.sum(delta, axis=0)

        self.grad_x = np.dot(delta, self.w.T)

class OutputLayer(BaseLayer):
    def forward(self, x):
        self.x = x
        u = np.dot(x, self.w) + self.b
        self.y = stable_softmax(u)

    def backward(self, t):
        delta = self.y - t

        self.grad_w = np.dot(self.x.T, delta)
        self.grad_b = np.sum(delta, axis=0)

        self.grad_x = np.dot(delta, self.w.T)


