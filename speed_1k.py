import numpy as np

import numpy_sugar as ns
from glimix_core.glmm import GLMMExpFam

if __name__ == '__main__':

    nsamples = 1000

    random = np.random.RandomState(2)
    X = random.randn(nsamples, nsamples + 1)
    X -= X.mean(0)
    X /= X.std(0)
    X /= np.sqrt(X.shape[1])

    K = X.dot(X.T)

    z = random.multivariate_normal(0.2 * np.ones(nsamples), 0.2 * K)
    QS = ns.linalg.economic_qs(K)

    ntri = random.randint(5, 30, nsamples)
    nsuc = np.zeros(nsamples, dtype=int)

    for (i, ni) in enumerate(ntri):
        nsuc[i] += sum(z[i] + 0.4 * random.randn(ni) > 0)

    ntri = np.ascontiguousarray(ntri)

    # glmm = GLMMExpFam(
    #     (nsuc, ntri),
    #     'binomial',
    #     np.ones((nsamples, 1)),
    #     QS,
    #     n_int=200,
    #     rtol=ns.epsilon.small * 1000 * 100,
    #     atol=ns.epsilon.small * 100)

    # 76.75s
    # glmm = GLMMExpFam((nsuc, ntri), 'binomial', np.ones((nsamples, 1)), QS)
    # glmm.fit(verbose=True)

    # 76.36s
    # glmm = GLMMExpFam((nsuc, ntri), 'binomial', np.ones((nsamples, 1)), QS)
    # glmm.fit(verbose=True, factr=1e6, pgtol=1e-3)

    # 73.96s
    # glmm = GLMMExpFam((nsuc, ntri), 'binomial', np.ones((nsamples, 1)), QS)
    # glmm.fit(verbose=True, factr=1e7, pgtol=1e-3)

    # 73.80s
    # glmm = GLMMExpFam((nsuc, ntri), 'binomial', np.ones((nsamples, 1)), QS)
    # glmm.fit(verbose=True, factr=1e7, pgtol=1e-2)

    # 56.77s
    # glmm = GLMMExpFam(
    #     (nsuc, ntri), 'binomial', np.ones((nsamples, 1)), QS, n_int=500)
    # glmm.fit(verbose=True, factr=1e7, pgtol=1e-2)

    # 35.54s
    # glmm = GLMMExpFam(
    #     (nsuc, ntri), 'binomial', np.ones((nsamples, 1)), QS, n_int=100)
    # glmm.fit(verbose=True, factr=1e7, pgtol=1e-2)

    # 50.08s
    # glmm = GLMMExpFam(
    #     (nsuc, ntri), 'binomial', np.ones((nsamples, 1)), QS, n_int=50)
    # glmm.fit(verbose=True, factr=1e7, pgtol=1e-2)

    # 27.66s
    glmm = GLMMExpFam(
        (nsuc, ntri),
        'binomial',
        np.ones((nsamples, 1)),
        QS,
        n_int=100,
        rtol=ns.epsilon.small * 1000 * 100,
        atol=ns.epsilon.small * 100)
    glmm.fit(verbose=True, factr=1e7, pgtol=1e-2)

    print(glmm.lml() + 2483.923312970759)
    print(glmm.scale - 4.211424061421387)
    print(glmm.delta - 0.013175939427293077)