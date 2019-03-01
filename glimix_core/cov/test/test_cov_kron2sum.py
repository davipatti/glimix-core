from numpy import array, concatenate, eye, kron
from numpy.linalg import slogdet
from numpy.random import RandomState
from numpy.testing import assert_allclose
from scipy.optimize import check_grad

from glimix_core._util import vec
from glimix_core.cov import Kron2SumCov


def test_kron2sumcov():
    G = array([[-1.5, 1.0], [-1.5, 1.0], [-1.5, 1.0]])
    Lr = array([[3], [2]], float)
    Ln = array([[1, 0], [2, 1]], float)

    cov = Kron2SumCov(2, 1)
    cov.G = G
    cov.Cr.L = Lr
    cov.Cn.L = Ln

    I = eye(G.shape[0])
    assert_allclose(
        cov.value(), kron(Lr @ Lr.T, G @ G.T) + kron(Ln @ Ln.T, I), atol=1e-4
    )
    assert_allclose(cov._check_grad(), 0, atol=1e-5)
    assert_allclose(cov.solve(cov.value()), eye(2 * G.shape[0]), atol=1e-7)
    assert_allclose(cov.logdet(), slogdet(cov.value())[1], atol=1e-7)
    assert_allclose(
        [cov.L[0, 0], cov.L[2, 3], cov.L[2, 1]],
        [0.23093921294934955, -5.2536114062217535e-17, 0.2828416166629259],
    )

    def func(x):
        cov.Cr.Lu = x[:2]
        cov.Cn.Lu = x[2:]
        return cov.logdet()

    def grad(x):
        cov.Cr.Lu = x[:2]
        cov.Cn.Lu = x[2:]
        D = cov.logdet_gradient()
        return concatenate((D["Cr.Lu"], D["Cn.Lu"]))

    random = RandomState(0)
    assert_allclose(check_grad(func, grad, random.randn(5)), 0, atol=1e-5)

    V = random.randn(3, 2)

    g = cov.Cr.gradient()["Lu"]
    g0 = cov.gradient_dot(vec(V), "Cr.Lu")
    for i in range(2):
        assert_allclose(g0[..., i], kron(g[..., i], G @ G.T) @ vec(V))

    g = cov.Cn.gradient()["Lu"]
    g0 = cov.gradient_dot(vec(V), "Cn.Lu")
    for i in range(3):
        assert_allclose(g0[..., i], kron(g[..., i], eye(3)) @ vec(V))

    V = random.randn(3, 2, 4)

    g = cov.Cr.gradient()["Lu"]
    g0 = cov.gradient_dot(vec(V), "Cr.Lu")
    for i in range(2):
        for j in range(4):
            assert_allclose(g0[j, ..., i], kron(g[..., i], G @ G.T) @ vec(V[..., j]))

    g = cov.Cn.gradient()["Lu"]
    g0 = cov.gradient_dot(vec(V), "Cn.Lu")
    for i in range(3):
        for j in range(4):
            assert_allclose(g0[j, ..., i], kron(g[..., i], eye(3)) @ vec(V[..., j]))


def test_kron2sumcov_g_full_col_rank():

    G = array([[-1.5, 1.0, 0.2, 0.5], [1.0, -0.25, -1.5, 1.0], [-0.1, -0.20, -2.5, 0]])
    Lr = array([[3], [2]], float)
    Ln = array([[1, 0], [2, 1]], float)

    cov = Kron2SumCov(2, 1)
    cov.G = G
    cov.Cr.L = Lr
    cov.Cn.L = Ln

    I = eye(G.shape[0])
    assert_allclose(
        cov.value(), kron(Lr @ Lr.T, G @ G.T) + kron(Ln @ Ln.T, I), atol=1e-4
    )
    assert_allclose(cov._check_grad(), 0, atol=1e-5)
    assert_allclose(cov.solve(cov.value()), eye(2 * G.shape[0]), atol=1e-7)
    assert_allclose(cov.logdet(), slogdet(cov.value())[1], atol=1e-7)

    cov = Kron2SumCov(2, 2)
    cov.G = G
    Lr = array([[3, 0.0], [-2, 0.4]], float)
    Ln = array([[1, 0], [2, 1]], float)
    cov.Cr.L = Lr
    cov.Cn.L = Ln

    I = eye(G.shape[0])
    assert_allclose(
        cov.value(), kron(Lr @ Lr.T, G @ G.T) + kron(Ln @ Ln.T, I), atol=1e-4
    )
    assert_allclose(cov._check_grad(), 0, atol=1e-5)
    assert_allclose(cov.solve(cov.value()), eye(2 * G.shape[0]), atol=1e-7)
    assert_allclose(cov.logdet(), slogdet(cov.value())[1], atol=1e-7)
