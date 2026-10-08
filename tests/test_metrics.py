import math

from src.anf import algebraic_degree, anf_expression, output_component
from src.avalanche import avalanche_matrix
from src.boolean_functions import identity_function, linear_mix, quadratic_mix
from src.confusion import confusion_score
from src.dependency import dependency_matrix
from src.diffusion import dependency_density, diffusion_score
from src.sac import sac_error, sac_score


def test_anf_or_function():
    def boolean_or(x):
        return x[0] | x[1]

    assert anf_expression(boolean_or, 2) == "x0 + x1 + x0*x1"
    assert algebraic_degree(boolean_or, 2) == 2


def test_identity_structural_metrics():
    D = dependency_matrix(identity_function, 3, 3)
    assert D == [[1, 0, 0], [0, 1, 0], [0, 0, 1]]
    assert diffusion_score(D) == 1
    assert math.isclose(dependency_density(D), 1 / 3)
    assert confusion_score(identity_function, 3, 3) == 0


def test_linear_mix_structural_metrics():
    D = dependency_matrix(linear_mix, 3, 3)
    assert D == [[1, 1, 0], [1, 1, 1], [1, 0, 1]]
    assert diffusion_score(D) == 2
    assert confusion_score(linear_mix, 3, 3) == 1


def test_quadratic_mix_degree_and_confusion():
    degrees = [algebraic_degree(output_component(quadratic_mix, j), 3) for j in range(3)]
    assert degrees == [2, 2, 2]
    assert confusion_score(quadratic_mix, 3, 3) == 3


def test_identity_fails_sac():
    A = avalanche_matrix(identity_function, 3, 3)
    assert A == [[1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
    assert sac_error(A) == 0.5
    assert sac_score(A) == 0.0
