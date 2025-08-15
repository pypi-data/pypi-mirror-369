import cupy as cp

class Loss(object):
  """Loss functions for NN class"""

  def __init__(self):
    pass

  def mse(self,yhat,y):
    return (yhat - y)**2

  def mse_derivative(self,yhat,y):
    if yhat.shape == y.shape:
      return yhat - y
    return yhat - cp.reshape(y,yhat.shape)

  def mse_alt(y,yhat):
    return cp.mean((y - yhat)**2)

  def mse_alt_derivative(y,yhat):
    if y.shape == yhat.shape:
      return y - yhat
    return cp.reshape(y,yhat.shape) - yhat

  def binary_crossentropy(self,y,yhat):
    return -(y * cp.log(yhat) + (1 - y) * cp.log(1 - yhat))

  # source https://www.python-unleashed.com/post/derivation-of-the-binary-cross-entropy-loss-gradient
  def binary_crossentropy_derivative(self,y,yhat):
    return yhat - y