import os
import sys
# Add the parent directory to the system path
DIR_PATH = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(DIR_PATH, '..'))

import numpy as np
import math
from io import StringIO

from ariths_gen.wire_components import (
    Wire,
    ConstantWireValue0,
    ConstantWireValue1,
    Bus
)

from ariths_gen.core.arithmetic_circuits import GeneralCircuit

from ariths_gen.multi_bit_circuits.adders import (
    UnsignedCarryLookaheadAdder,
    UnsignedPGRippleCarryAdder,
    UnsignedRippleCarryAdder,
    SignedCarryLookaheadAdder,
    SignedPGRippleCarryAdder,
    SignedRippleCarryAdder,
    UnsignedCarrySkipAdder,
    SignedCarrySkipAdder,
    UnsignedKoggeStoneAdder,
    SignedKoggeStoneAdder,
    UnsignedBrentKungAdder,
    SignedBrentKungAdder,
    UnsignedSklanskyAdder,
    SignedSklanskyAdder,
    UnsignedHanCarlsonAdder,
    SignedHanCarlsonAdder,
    UnsignedLadnerFischerAdder,
    SignedLadnerFischerAdder,
    UnsignedKnowlesAdder,
    SignedKnowlesAdder,
    UnsignedCarrySelectAdder,
    SignedCarrySelectAdder,
    UnsignedConditionalSumAdder,
    SignedConditionalSumAdder,
    UnsignedCarryIncrementAdder,
    SignedCarryIncrementAdder
)

from ariths_gen.multi_bit_circuits.subtractors import (
    UnsignedRippleBorrowSubtractor,
    UnsignedRippleCarrySubtractor,
    SignedRippleBorrowSubtractor,
    SignedRippleCarrySubtractor
)

from ariths_gen.multi_bit_circuits.multipliers import (
    UnsignedDaddaMultiplier,
    UnsignedArrayMultiplier,
    UnsignedWallaceMultiplier,
    UnsignedCarrySaveMultiplier,
    SignedArrayMultiplier,
    SignedDaddaMultiplier,
    SignedWallaceMultiplier,
    SignedCarrySaveMultiplier
)


from ariths_gen.multi_bit_circuits.approximate_multipliers import (
    UnsignedTruncatedArrayMultiplier,
    UnsignedTruncatedCarrySaveMultiplier,
    UnsignedBrokenArrayMultiplier,
    UnsignedBrokenCarrySaveMultiplier
)

from ariths_gen.core.cgp_circuit import UnsignedCGPCircuit, SignedCGPCircuit


def test_cgp_unsigned_add():
    """ Test unsigned adders """
    N = 7
    a = Bus(N=N, prefix="a")
    b = Bus(N=N, prefix="b")
    av = np.arange(2**N)
    bv = av.reshape(-1, 1)
    expected = av + bv

    # Non configurable multi-bit adders
    for c in [UnsignedPGRippleCarryAdder, UnsignedRippleCarryAdder, UnsignedConditionalSumAdder, UnsignedKoggeStoneAdder, UnsignedBrentKungAdder, UnsignedSklanskyAdder]:
        add = c(a, b)
        code = StringIO()
        add.get_cgp_code_flat(code)
        cgp_code = code.getvalue()
        print(cgp_code)

        add2 = UnsignedCGPCircuit(cgp_code, [N, N])
        o = StringIO()
        add2.get_v_code_flat(o)
        print(o.getvalue())

        r = add2(av, bv)
        assert add(0, 0) == 0
        assert add2(0, 0) == 0
        np.testing.assert_array_equal(expected, r)

    # Multi-bit adders with configurable (uniform) logic blocks for parallel prefix computation (the adder will use the block_size argument it recognizes, others are ignored)
    for c in [UnsignedCarryLookaheadAdder, UnsignedCarrySkipAdder, UnsignedCarrySelectAdder, UnsignedCarryIncrementAdder]:
        for bs in range(1, N+1):
            add = c(a, b, cla_block_size=bs, bypass_block_size=bs, select_block_size=bs, increment_block_size=bs)
            r = add(av, bv)
            code = StringIO()
            add.get_cgp_code_flat(code)
            cgp_code = code.getvalue()
            print(cgp_code)

            add2 = UnsignedCGPCircuit(cgp_code, [N, N])
            o = StringIO()
            add2.get_v_code_flat(o)
            print(o.getvalue())

            r = add2(av, bv)
            assert add(0, 0) == 0
            assert add2(0, 0) == 0
            np.testing.assert_array_equal(expected, r)

    # Multi-bit tree adders with configurable structure based on input bit width (2 configs tested here for the 9-bitwidth input)
    for c in [UnsignedHanCarlsonAdder, UnsignedKnowlesAdder, UnsignedLadnerFischerAdder]:
        for config in range(1, (math.ceil(math.log(N, 2))-2)+1):
            add = c(a, b, config_choice=config)
            r = add(av, bv)
            code = StringIO()
            add.get_cgp_code_flat(code)
            cgp_code = code.getvalue()
            print(cgp_code)

            add2 = UnsignedCGPCircuit(cgp_code, [N, N])
            o = StringIO()
            add2.get_v_code_flat(o)
            print(o.getvalue())

            r = add2(av, bv)
            assert add(0, 0) == 0
            assert add2(0, 0) == 0
            np.testing.assert_array_equal(expected, r)


def test_cgp_signed_add():
    """ Test signed adders """
    N = 7
    a = Bus(N=N, prefix="a")
    b = Bus(N=N, prefix="b")
    av = np.arange(-(2**(N-1)), 2**(N-1))
    bv = av.reshape(-1, 1)
    expected = av + bv

    # Non configurable multi-bit adders
    for c in [SignedPGRippleCarryAdder, SignedRippleCarryAdder, SignedConditionalSumAdder, SignedKoggeStoneAdder, SignedBrentKungAdder, SignedSklanskyAdder]:
        add = c(a, b)
        r = add(av, bv)
        code = StringIO()
        add.get_cgp_code_flat(code)
        cgp_code = code.getvalue()
        print(cgp_code)

        add2 = SignedCGPCircuit(cgp_code, [N, N])
        o = StringIO()
        add2.get_v_code_flat(o)
        print(o.getvalue())

        r = add2(av, bv)
        assert add(0, 0) == 0
        assert add2(0, 0) == 0
        np.testing.assert_array_equal(expected, r)

    # Multi-bit adders with configurable (uniform) logic blocks for parallel prefix computation (the adder will use the block_size argument it recognizes, others are ignored)
    for c in [SignedCarryLookaheadAdder, SignedCarrySkipAdder, SignedCarrySelectAdder, SignedCarryIncrementAdder]:
        for bs in range(1, N+1):
            add = c(a, b, cla_block_size=bs, bypass_block_size=bs, select_block_size=bs, increment_block_size=bs)
            r = add(av, bv)
            code = StringIO()
            add.get_cgp_code_flat(code)
            cgp_code = code.getvalue()
            print(cgp_code)

            add2 = SignedCGPCircuit(cgp_code, [N, N])
            o = StringIO()
            add2.get_v_code_flat(o)
            print(o.getvalue())

            r = add2(av, bv)
            assert add(0, 0) == 0
            assert add2(0, 0) == 0
            np.testing.assert_array_equal(expected, r)

    # Multi-bit tree adders with configurable structure based on input bit width (2 configs tested here for the 9-bitwidth input)
    for c in [SignedHanCarlsonAdder, SignedKnowlesAdder, SignedLadnerFischerAdder]:
        for config in range(1, (math.ceil(math.log(N, 2))-2)+1):
            add = c(a, b, config_choice=config)
            r = add(av, bv)
            code = StringIO()
            add.get_cgp_code_flat(code)
            cgp_code = code.getvalue()
            print(cgp_code)

            add2 = SignedCGPCircuit(cgp_code, [N, N])
            o = StringIO()
            add2.get_v_code_flat(o)
            print(o.getvalue())

            r = add2(av, bv)
            assert add(0, 0) == 0
            assert add2(0, 0) == 0
            np.testing.assert_array_equal(expected, r)


def test_cgp_unsigned_sub():
    """ Test unsigned subtractors """
    N = 7
    a = Bus(N=N, prefix="a")
    b = Bus(N=N, prefix="b")
    av = np.arange(2**N)
    bv = av.reshape(-1, 1)
    expected = av - bv

    #for c in [UnsignedRippleBorrowSubtractor, UnsignedRippleCarrySubtractor]:
    for c in [UnsignedRippleBorrowSubtractor]:
        sub = c(a, b)
        code = StringIO()
        sub.get_cgp_code_flat(code)
        cgp_code = code.getvalue()

        sub2 = UnsignedCGPCircuit(cgp_code, [N, N], signed_out=True)
        o = StringIO()
        sub2.get_v_code_flat(o)
        print(o.getvalue())

        r = sub2(av, bv)
        assert sub(0, 0) == 0
        assert sub2(0, 0) == 0
        np.testing.assert_array_equal(expected, r)
    

def test_cgp_signed_sub():
    """ Test signed subtractors """
    N = 7
    a = Bus(N=N, prefix="a")
    b = Bus(N=N, prefix="b")
    av = np.arange(-(2**(N-1)), 2**(N-1))
    bv = av.reshape(-1, 1)
    expected = av - bv

    for c in [SignedRippleBorrowSubtractor, SignedRippleCarrySubtractor]:
        sub = c(a, b)
        r = sub(av, bv)
        code = StringIO()
        sub.get_cgp_code_flat(code)
        cgp_code = code.getvalue()
        print(cgp_code)

        sub2 = SignedCGPCircuit(cgp_code, [N, N])
        o = StringIO()
        sub2.get_v_code_flat(o)
        print(o.getvalue())

        r = sub2(av, bv)
        assert sub(0, 0) == 0
        assert sub2(0, 0) == 0
        np.testing.assert_array_equal(expected, r)


def test_cgp_unsigned_mul():
    """ Test unsigned multipliers """
    N = 7
    a = Bus(N=N, prefix="a")
    b = Bus(N=N, prefix="b")
    av = np.arange(2**N)
    bv = av.reshape(-1, 1)
    expected = av * bv

    # No configurability
    for c in [UnsignedArrayMultiplier]:
        mul = c(a, b)
        code = StringIO()
        mul.get_cgp_code_flat(code)
        cgp_code = code.getvalue()

        mul2 = UnsignedCGPCircuit(cgp_code, [N, N])
        r = mul2(av, bv)

        assert mul(0, 0) == 0
        assert mul2(0, 0) == 0
        np.testing.assert_array_equal(expected, r)

    # Configurable PPA
    for c in [UnsignedDaddaMultiplier, UnsignedCarrySaveMultiplier, UnsignedWallaceMultiplier]:
        # Non configurable multi-bit adders
        for ppa in [UnsignedPGRippleCarryAdder, UnsignedRippleCarryAdder, UnsignedConditionalSumAdder, UnsignedKoggeStoneAdder, UnsignedBrentKungAdder, UnsignedSklanskyAdder]:
            # Test first the array wallace tree implementation (using more HAs/FAs than CSA implementation)
            if c == UnsignedWallaceMultiplier:
                mul = c(a, b, unsigned_adder_class_name=ppa, use_csa=False)
                code = StringIO()
                mul.get_cgp_code_flat(code)
                cgp_code = code.getvalue()

                mul2 = UnsignedCGPCircuit(cgp_code, [N, N])
                r = mul2(av, bv)

                assert mul(0, 0) == 0
                assert mul2(0, 0) == 0
                np.testing.assert_array_equal(expected, r)

            mul = c(a, b, unsigned_adder_class_name=ppa)
            code = StringIO()
            mul.get_cgp_code_flat(code)
            cgp_code = code.getvalue()

            mul2 = UnsignedCGPCircuit(cgp_code, [N, N])
            r = mul2(av, bv)

            assert mul(0, 0) == 0
            assert mul2(0, 0) == 0
            np.testing.assert_array_equal(expected, r)

        # Multi-bit adders with configurable (uniform) logic blocks for parallel prefix computation (the ppa will use the block_size argument it recognizes, others are ignored)
        for ppa in [UnsignedCarryLookaheadAdder, UnsignedCarrySkipAdder, UnsignedCarrySelectAdder, UnsignedCarryIncrementAdder]:
            for i in range(1, N+1):
                # Test first the array wallace tree implementation (using more HAs/FAs than CSA implementation)
                if c == UnsignedWallaceMultiplier:
                    mul = c(a, b, unsigned_adder_class_name=ppa, use_csa=False, cla_block_size=i, bypass_block_size=i, select_block_size=i, increment_block_size=i)
                    code = StringIO()
                    mul.get_cgp_code_flat(code)
                    cgp_code = code.getvalue()

                    mul2 = UnsignedCGPCircuit(cgp_code, [N, N])
                    r = mul2(av, bv)

                    assert mul(0, 0) == 0
                    assert mul2(0, 0) == 0
                    np.testing.assert_array_equal(expected, r)

                mul = c(a, b, unsigned_adder_class_name=ppa, cla_block_size=i, bypass_block_size=i, select_block_size=i, increment_block_size=i)
                code = StringIO()
                mul.get_cgp_code_flat(code)
                cgp_code = code.getvalue()

                mul2 = UnsignedCGPCircuit(cgp_code, [N, N])
                r = mul2(av, bv)

                assert mul(0, 0) == 0
                assert mul2(0, 0) == 0
                np.testing.assert_array_equal(expected, r)

        # Multi-bit tree adders with configurable structure based on input bit width (NOTE for showcase here, the second config would be applicable from bit width 9 onward; not tested here for the sake of saving deployment testing time)
        for adder in [UnsignedHanCarlsonAdder, UnsignedKnowlesAdder, UnsignedLadnerFischerAdder]:
            for i in range(1, N+1):
                # Test first the array wallace tree implementation (using more HAs/FAs than CSA implementation)
                if c == UnsignedWallaceMultiplier:
                    mul = c(a, b, unsigned_adder_class_name=ppa, use_csa=False, config_choice=1)
                    code = StringIO()
                    mul.get_cgp_code_flat(code)
                    cgp_code = code.getvalue()

                    mul2 = UnsignedCGPCircuit(cgp_code, [N, N])
                    r = mul2(av, bv)

                    assert mul(0, 0) == 0
                    assert mul2(0, 0) == 0
                    np.testing.assert_array_equal(expected, r)

                mul = c(a, b, unsigned_adder_class_name=ppa, config_choice=1)
                code = StringIO()
                mul.get_cgp_code_flat(code)
                cgp_code = code.getvalue()

                mul2 = UnsignedCGPCircuit(cgp_code, [N, N])
                r = mul2(av, bv)

                assert mul(0, 0) == 0
                assert mul2(0, 0) == 0
                np.testing.assert_array_equal(expected, r)


def test_cgp_signed_mul():
    """ Test signed multipliers """
    N = 7
    a = Bus(N=N, prefix="a")
    b = Bus(N=N, prefix="b")
    av = np.arange(-(2**(N-1)), 2**(N-1))
    bv = av.reshape(-1, 1)
    expected = av * bv

    # No configurability
    for c in [SignedArrayMultiplier]:
        mul = c(a, b)
        code = StringIO()
        mul.get_cgp_code_flat(code)
        cgp_code = code.getvalue()

        mul2 = SignedCGPCircuit(cgp_code, [N, N])
        r = mul2(av, bv)

        assert mul(0, 0) == 0
        assert mul2(0, 0) == 0
        np.testing.assert_array_equal(expected, r)

    # Configurable PPA
    for c in [SignedDaddaMultiplier, SignedCarrySaveMultiplier, SignedWallaceMultiplier]:
        # Non configurable multi-bit adders
        for ppa in [UnsignedPGRippleCarryAdder, UnsignedRippleCarryAdder, UnsignedConditionalSumAdder, UnsignedKoggeStoneAdder, UnsignedBrentKungAdder, UnsignedSklanskyAdder]:
            # Test first the array wallace tree implementation (using more HAs/FAs than CSA implementation)
            if c == UnsignedWallaceMultiplier:
                mul = c(a, b, unsigned_adder_class_name=ppa, use_csa=False)
                code = StringIO()
                mul.get_cgp_code_flat(code)
                cgp_code = code.getvalue()

                mul2 = SignedCGPCircuit(cgp_code, [N, N])
                r = mul2(av, bv)

                assert mul(0, 0) == 0
                assert mul2(0, 0) == 0
                np.testing.assert_array_equal(expected, r)

            mul = c(a, b, unsigned_adder_class_name=ppa)
            code = StringIO()
            mul.get_cgp_code_flat(code)
            cgp_code = code.getvalue()

            mul2 = SignedCGPCircuit(cgp_code, [N, N])
            r = mul2(av, bv)

            assert mul(0, 0) == 0
            assert mul2(0, 0) == 0
            np.testing.assert_array_equal(expected, r)

        # Multi-bit adders with configurable (uniform) logic blocks for parallel prefix computation (the ppa will use the block_size argument it recognizes, others are ignored)
        for ppa in [UnsignedCarryLookaheadAdder, UnsignedCarrySkipAdder, UnsignedCarrySelectAdder, UnsignedCarryIncrementAdder]:
            for bs in range(1, N+1):
                # Test first the array wallace tree implementation (using more HAs/FAs than CSA implementation)
                if c == UnsignedWallaceMultiplier:
                    mul = c(a, b, unsigned_adder_class_name=ppa, use_csa=False, cla_block_size=bs, bypass_block_size=bs, select_block_size=bs, increment_block_size=bs)
                    code = StringIO()
                    mul.get_cgp_code_flat(code)
                    cgp_code = code.getvalue()

                    mul2 = SignedCGPCircuit(cgp_code, [N, N])
                    r = mul2(av, bv)

                    assert mul(0, 0) == 0
                    assert mul2(0, 0) == 0
                    np.testing.assert_array_equal(expected, r)

                mul = c(a, b, unsigned_adder_class_name=ppa, cla_block_size=bs, bypass_block_size=bs, select_block_size=bs, increment_block_size=bs)
                code = StringIO()
                mul.get_cgp_code_flat(code)
                cgp_code = code.getvalue()

                mul2 = SignedCGPCircuit(cgp_code, [N, N])
                r = mul2(av, bv)

                assert mul(0, 0) == 0
                assert mul2(0, 0) == 0
                np.testing.assert_array_equal(expected, r)

        # Multi-bit tree adders with configurable structure based on input bit width (NOTE for showcase here, the second config would be applicable from bit width 9 onward; not tested here for the sake of saving deployment testing time)
        for ppa in [UnsignedHanCarlsonAdder, UnsignedKnowlesAdder, UnsignedLadnerFischerAdder]:
            for i in range(1, N+1):
                # Test first the array wallace tree implementation (using more HAs/FAs than CSA implementation)
                if c == UnsignedWallaceMultiplier:
                    mul = c(a, b, unsigned_adder_class_name=ppa, use_csa=False, config_choice=1)
                    code = StringIO()
                    mul.get_cgp_code_flat(code)
                    cgp_code = code.getvalue()

                    mul2 = SignedCGPCircuit(cgp_code, [N, N])
                    r = mul2(av, bv)

                    assert mul(0, 0) == 0
                    assert mul2(0, 0) == 0
                    np.testing.assert_array_equal(expected, r)

                mul = c(a, b, unsigned_adder_class_name=ppa, config_choice=1)
                code = StringIO()
                mul.get_cgp_code_flat(code)
                cgp_code = code.getvalue()

                mul2 = SignedCGPCircuit(cgp_code, [N, N])
                r = mul2(av, bv)

                assert mul(0, 0) == 0
                assert mul2(0, 0) == 0
                np.testing.assert_array_equal(expected, r)


def test_cgp_variant1():
    # one input is connected to the output (first bit)
    cgp = "{16,9,37,1,2,1,0}([18]15,12,1)([19]7,7,4)([20]3,12,5)([21]17,3,0)([22]8,14,3)([23]15,3,6)([24]14,0,2)([25]9,9,5)([26]17,13,1)([27]12,13,0)([28]7,16,8)([29]12,11,0)([30]5,13,3)([31]5,13,2)([32]30,12,5)([33]30,29,2)([34]31,33,3)([35]6,14,4)([36]6,14,2)([37]35,34,4)([38]35,34,2)([39]36,38,3)([40]7,15,4)([41]7,15,2)([42]40,39,4)([43]40,39,2)([44]41,43,3)([45]8,16,4)([46]8,16,2)([47]45,44,4)([48]45,44,2)([49]46,48,3)([50]9,17,4)([51]9,17,2)([52]50,49,4)([53]50,49,2)([54]51,53,3)(11,40,33,32,37,42,47,52,54)"

    c = UnsignedCGPCircuit(cgp, [8, 8], name="cgp_circuit")
    assert c(0, 0) == 8  # TypeError: 'int' object is not subscriptable


if __name__ == "__main__":
    test_cgp_unsigned_add()
    test_cgp_signed_add()
    test_cgp_unsigned_sub()
    test_cgp_signed_sub()
    test_cgp_unsigned_mul()
    test_cgp_signed_mul()
    test_cgp_variant1()
    print("CGP Python tests were successful!")
