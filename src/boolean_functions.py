"""Hand-designed toy Boolean transformations used as controlled baselines."""


def sample_function(x):
    x0, x1, x2 = x
    return [
        x0 ^ x1,
        x1 ^ x2,
        (x0 & x2) ^ x1,
    ]


def identity_function(x):
    return list(x)


def linear_mix(x):
    x0, x1, x2 = x
    return [
        x0 ^ x1 ^ x2,
        x0 ^ x1,
        x1 ^ x2,
    ]


def quadratic_mix(x):
    x0, x1, x2 = x
    return [
        x0 ^ (x1 & x2),
        x1 ^ (x0 & x2),
        x2 ^ (x0 & x1),
    ]


def uneven_nonlinear(x):
    x0, x1, x2 = x
    return [
        x0 ^ (x1 & x2),
        x0 ^ x1,
        x0 ^ x2,
    ]


def cubic_mix(x):
    x0, x1, x2 = x
    cubic = x0 & x1 & x2
    return [
        x0 ^ x1 ^ cubic,
        x1 ^ x2 ^ cubic,
        x2 ^ x0 ^ cubic,
    ]
