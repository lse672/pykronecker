from __future__ import annotations

import sys
import os

import pytest

from pykronecker.block import KroneckerBlock, KroneckerBlockDiag
from pykronecker.utils import vec

sys.path.append(os.path.dirname(os.path.realpath(__file__)))

import numpy as np
from utils import assert_universal, generate_test_data, assert_pow, assert_pow_fails, assert_inv, assert_inv_fails

np.set_printoptions(precision=3, linewidth=500, threshold=500, suppress=True, edgeitems=5)


def test_block():

    X, Y, P, kp_literal, ks_literal, kd_literal, kp_optimised, ks_optimised, kd_optimised = generate_test_data()
    x = np.concatenate([vec(X), vec(Y)])
    Q = np.concatenate([P, P], axis=0)

    kb_literal1 = np.block([[kp_literal, kd_literal], [np.zeros(kp_literal.shape), ks_literal]])
    kb_optimised1 = KroneckerBlock([[kp_optimised, kd_optimised], [np.zeros(kp_literal.shape), ks_optimised]])

    kb_literal2 = np.block([[kp_literal, kd_literal], [kd_literal, kp_literal]])
    kb_optimised2 = KroneckerBlock([[kp_optimised, kd_optimised], [kd_optimised, kp_optimised]])

    assert_universal(x, Q, kb_literal1, kb_optimised1)
    assert_universal(x, Q, kb_literal2, kb_optimised2)

    with pytest.raises(ValueError):
        KroneckerBlock([[['a', 'b']]])

    with pytest.raises(ValueError):
        kb_optimised1 @ np.random.randn(5, 5, 5)

    with pytest.raises(ValueError):
        kb_optimised2 @ np.random.randn(5, 5, 5)

    assert_pow_fails(kb_optimised1)
    assert_pow(kb_literal2, kb_optimised2)

    assert_inv_fails(kb_optimised1)
    assert_inv_fails(kb_optimised2)







def test_block_diag():

    X, Y, P, kp_literal, ks_literal, kd_literal, kp_optimised, ks_optimised, kd_optimised = generate_test_data()
    x = np.concatenate([vec(X), vec(Y)])
    Q = np.concatenate([P, P], axis=0)
    d = np.concatenate([vec(X), vec(Y), np.random.randn(5)])
    D = np.concatenate([P, P,  np.random.randn(5, 5)], axis=0)

    kbd_literal1 = np.block([[kp_literal, np.zeros(kp_literal.shape)], [np.zeros(kp_literal.shape), ks_literal]])
    kbd_optimised1 = KroneckerBlockDiag([kp_optimised, ks_optimised])

    N = kp_literal.shape[0]
    kbd_literal2 = np.block([[kp_literal, np.zeros(kp_literal.shape), np.zeros((N, 5))],
                             [np.zeros(kp_literal.shape), kp_literal, np.zeros((N, 5))],
                             [np.zeros((5, N)), np.zeros((5, N)), np.eye(5)]])
    kbd_optimised2 = KroneckerBlockDiag([kp_optimised, kp_optimised, np.eye(5)])

    assert_universal(x, Q, kbd_literal1, kbd_optimised1)
    assert_universal(d, D, kbd_literal2, kbd_optimised2)

    assert_pow_fails(kbd_optimised1)
    assert_pow(kbd_literal2, kbd_optimised2)

    assert_inv_fails(kbd_optimised1)
    assert_inv(kbd_literal2, kbd_optimised2)

    with pytest.raises(ValueError):
        kbd_optimised1 @ np.random.randn(5, 5, 5)

    with pytest.raises(ValueError):
        kbd_optimised2 @ np.random.randn(5, 5, 5)

