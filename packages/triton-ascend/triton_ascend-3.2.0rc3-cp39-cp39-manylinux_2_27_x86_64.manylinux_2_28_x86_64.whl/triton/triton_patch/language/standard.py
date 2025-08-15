from math import pi as math_pi
from triton.language import core, math
from triton.language import float32, int1
from triton.language.standard import max, sum
from triton.runtime.jit import jit
from triton.language.extra.ascend.libdevice import flip as ascend_flip



@core._tensor_member_fn
@jit
def flip(x, dim=None):
    """
    Flips a tensor `x` along the dimension `dim`.

    :param x: the first input tensor
    :type x: Block
    :param dim: the dimension to flip along (currently only final dimension supported)
    :type dim: int
    """
    return ascend_flip(x, dim)

@core._tensor_member_fn
@jit
@math._add_math_1arg_docstr("sigmoid")
def sigmoid(x):
    _is_floating_type: core.constexpr = x.dtype.is_floating()
    core.static_assert(_is_floating_type == True, f"Expected dtype fp16/fp32/bf16, but got {core.constexpr(x.dtype)}")
    return (1 / (1 + math.exp(-x.to(core.float32)))).to(x.dtype)

@core._tensor_member_fn
@jit
@math._add_math_1arg_docstr("softmax")
def softmax(x, ieee_rounding=False):
    _is_floating_type: core.constexpr = x.dtype.is_floating()
    core.static_assert(_is_floating_type == True, f"Expected dtype fp16/fp32/bf16, but got {core.constexpr(x.dtype)}")
    z = x.to(core.float32) - max(x, 0)
    num = math.exp(z)
    den = sum(num, 0)
    return math.fdiv(num, den, ieee_rounding).to(x.dtype)

@core._tensor_member_fn
@jit
@math._add_math_1arg_docstr("isfinited")
def isfinited(x):
    _is_floating_type: core.constexpr = x.dtype.is_floating()
    core.static_assert(_is_floating_type == True, f"Expected dtype fp16/fp32/bf16, but got {core.constexpr(x.dtype)}")
    nan_mask = math.isnan(x)
    inf_mask = math.isinf(x)
    return (~nan_mask & ~inf_mask).to(int1)

@core._tensor_member_fn
@jit
@math._add_math_1arg_docstr("finitef")
def finitef(x):
    core.static_assert(x.dtype == float32, f"finitef only supports float32, but got {core.constexpr(x.dtype)}")
    nan_mask = math.isnan(x)
    inf_mask = math.isinf(x)
    return (~nan_mask & ~inf_mask).to(int1)

@core._tensor_member_fn
@jit
@math._add_math_1arg_docstr("rint")
def rint(x):
    _is_floating_type: core.constexpr = x.dtype.is_floating()
    core.static_assert(_is_floating_type == True, f"Expected dtype fp16/fp32/bf16, but got {core.constexpr(x.dtype)}")
    return core.where(x >= 0, math.floor(x + 0.5), math.ceil(x - 0.5))

pi: core.constexpr = math_pi

@core._tensor_member_fn
@jit
@math._add_math_2arg_docstr("atan2")
def atan2(y, x):
    _is_floating_type_x: core.constexpr = x.dtype.is_floating()
    core.static_assert(_is_floating_type_x == True, f"Expected dtype fp16/fp32/bf16, but got {core.constexpr(x.dtype)}")
    _is_floating_type_y: core.constexpr = y.dtype.is_floating()
    core.static_assert(_is_floating_type_y == True, f"Expected dtype fp16/fp32/bf16, but got {core.constexpr(y.dtype)}")
    half_pi: core.constexpr = 0.5 * pi
    base = core.where(x == 0, 0.0, math.atan(y.to(float32) / x.to(float32)))
    base = core.where((x == 0) & (y > 0), half_pi, base)
    base = core.where((x == 0) & (y < 0), -half_pi, base)

    add_pi = core.where((x < 0) & (y >= 0), pi, 0.0)
    sub_pi = core.where((x < 0) & (y < 0), -pi, 0.0)
    return (base + add_pi + sub_pi).to(x.dtype)
