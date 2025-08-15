def test_dense_forward_backward():
    from buildai_pro.nn import Dense
    from buildai_pro.tensor import Tensor
    l = Dense(3,2)
    x = Tensor([1,2,3])
    out = l.forward(x)
    assert len(out.data) == 2
    grad = Tensor([1.0, -1.0])
    gin = l.backward(grad)
    assert len(gin.data) == 3
