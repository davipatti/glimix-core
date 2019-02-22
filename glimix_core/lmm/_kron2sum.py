from numpy import asfortranarray, log, sqrt

from glimix_core.cov import Kron2SumCov
from glimix_core.mean import KronMean
from glimix_core.util import log2pi, vec
from optimix import Function


class Kron2Sum(Function):
    def __init__(self, Y, A, F, G, rank=1):
        """ LMM for multiple multiple traits.

        Let n, c, and p be the number of samples, covariates, and traits, respectively.
        The outcome variable is a n×p matrix distributed according to

            vec(Y) ~ N((𝐀 ⊗ 𝐅) vec(𝐁), Cᵣ ⊗ GGᵗ + Cₙ ⊗ I).

        𝐀 and 𝐅 are design matrices of dimensions p×p and n×c provided by the user,
        where 𝐅 is the usual matrix of covariates.
        𝐁 is a p×c matrix of fixed-effect sizes.
        G is a n×r matrix provided by the user and I is a n×n identity matrices.
        Cᵣ and Cₙ are both symmetric matrices of dimensions p×p, for which Cₙ is
        guaranteed by our implementation to be full rank.
        The parameters of this model are the matrices 𝐁, Cᵣ, and Cₙ.
        """
        Y = asfortranarray(Y)
        self._Y = Y
        self._y = Y.ravel(order="F")
        self._A = A
        self._F = F
        self._cov = Kron2SumCov(Y.shape[1], rank)
        self._cov.G = G
        self._mean = KronMean(F.shape[1], Y.shape[1])
        self._mean.A = A
        self._mean.F = F
        Cr_Lu = self._cov.variables().get("Cr_Lu")
        Cn_Lu = self._cov.variables().get("Cn_Lu")
        Function.__init__(self, Cr_Lu=Cr_Lu, Cn_Lu=Cn_Lu)
        self.set_nodata()

    @property
    def mean(self):
        return self._mean

    @property
    def cov(self):
        return self._cov

    @property
    def nsamples(self):
        """ Number of samples. """
        return self._Y.shape[0]

    @property
    def ntraits(self):
        """ Number of traits. """
        return self._Y.shape[1]

    @property
    def ncovariates(self):
        """ Number of covariates. """
        return self._F.shape[1]

    def value(self):
        return self.lml()

    def gradient(self):
        grad = self.lml_gradient()
        return grad

    def lml(self):
        r"""Log of the marginal likelihood.

        Returns
        -------
        float
            Log of the marginal likelihood.
        """
        breakpoint()
        np = self.nsamples * self.ntraits
        lml = -np * log2pi - self._cov.logdet()

        m = vec(self._mean.feed().value())
        d = self._y - m
        dKid = d @ self._cov.solve(d)
        lml -= dKid

        return lml / 2

    def lml_gradient(self):
        ld_grad = self._cov.logdet_gradient()
        dK = self._cov.compact_gradient()
        Kiy = self._cov.solve(self._y)
        m = vec(self._mean.feed().value())
        Kim = self._cov.solve(m)
        grad = {}
        for var in ["Cr_Lu", "Cn_Lu"]:
            grad[var] = -ld_grad[var]
            grad[var] += Kiy.T @ dK[var] @ Kiy
            grad[var] -= 2 * (Kim.T @ dK[var] @ Kiy)
            grad[var] += Kim.T @ dK[var] @ Kim
            grad[var] /= 2
        return grad

    @property
    def z(self):
        return self._cov.L @ self._y

    def fit(self, verbose=True):
        r"""Maximise the marginal likelihood.

        Parameters
        ----------
        verbose : bool, optional
            ``True`` for progress output; ``False`` otherwise.
            Defaults to ``True``.
        """
        # self._verbose = verbose
        self.feed().maximize(verbose=verbose)
        # self.delta = self._get_delta()
        # self._update_fixed_effects()
        # self._verbose = False