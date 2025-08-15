from typing import *
import asyncio
import logging
import traceback
import sys
from functools import reduce

import math
import cmath
import numpy as np

from .exception import HashError
from .utils import DEBUG


def method01(a, b, c):
    try:
        return round(math.sin(a) * math.cos(b) * math.tan(c) + math.log(a + b + c))
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method02(a, b, c):
    try:
        return round(math.exp(a) * math.sqrt(b) * math.pow(c, 3) + math.gamma(a + b + c))
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method03(a, b, c):
    try:
        return round(math.erf(a) * math.erfc(b) * math.erfi(c) + math.lgamma(a + b + c))
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method04(a, b, c):
    try:
        return round(math.sinh(a) * math.cosh(b) * math.tanh(c) + math.log1p(a + b + c))
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method05(a, b, c):
    try:
        return round(math.asin(a / (a + b + c)) * math.acos(b / (a + b + c)) * math.atan(c / (a + b + c)))
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method06(a, b, c):
    try:
        result = (a ** 7 + b ** 8 + c ** 9) * math.sinh(a) * math.cosh(b) * math.tanh(c)
        result += (a * b * c) ** (1/8) * math.log10(a + b + c + 1)
        result *= math.exp(a / (b + c + 1))
        result = int(result)
        return result
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method07(a, b, c):
    try:
        result = (a ** 8 + b ** 9 + c ** 10) * math.asin(a / (a + 1)) * math.acos(b / (b + 1)) * math.atan(c / (c + 1))
        result += (a * b * c) ** (1/9) * math.log2(a + b + c + 1)
        result *= math.exp(a / (b + c + 1))
        result = int(result)
        return result
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method08(a, b, c):
    try:
        result = (a ** 9 + b ** 10 + c ** 11) * math.asinh(a / (a + 1)) * math.acosh(b / (b + 1)) * math.atanh(c / (c + 1))
        result += (a * b * c) ** (1/10) * math.log1p(a + b + c)
        result *= math.exp(a / (b + c + 1))
        result = int(result)
        return result
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method09(a, b, c):
    try:
        result = (a ** 10 + b ** 11 + c ** 12) * math.sin(a) * math.cos(b) * math.tan(c)
        result += (a * b * c) ** (1/11) * math.log(a + b + c + 1)
        result *= math.exp(a / (b + c + 1))
        result = int(result)
        return result
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method10(a, b, c):
    try:
        result = (a ** 11 + b ** 12 + c ** 13) * math.sinh(a) * math.cosh(b) * math.tanh(c)
        result += (a * b * c) ** (1/12) * math.log10(a + b + c + 1)
        result *= math.exp(a / (b + c + 1))
        result = int(result)
        return result
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method11(a, b, c):
    try:
        result = (a ** 3 + b ** 2 + c) * math.log(a + b + c + 1)
        result += (a * b * c) ** (1/3) * math.sin(a + b + c)
        result *= math.exp(a / (b + c + 1))
        result = int(result)
        return result
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method12(a, b, c):
    try:
        result = (a ** 2 + b ** 3 + c ** 4) * math.cos(a + b + c)
        result += (a * b * c) ** (1/2) * math.tan(a + b + c)
        result *= math.log(a + b + c + 1)
        result = int(result)
        return result
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method13(a, b, c):
    try:
        result = (a ** 4 + b ** 5 + c ** 6) * math.sinh(a + b + c)
        result += (a * b * c) ** (1/4) * math.cosh(a + b + c)
        result *= math.exp(a / (b + c + 1))
        result = int(result)
        return result
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method14(a, b, c):
    try:
        result = (a ** 5 + b ** 6 + c ** 7) * math.tanh(a + b + c)
        result += (a * b * c) ** (1/5) * math.asin(a / (b + c + 1))
        result *= math.log(a + b + c + 1)
        result = int(result)
        return result
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method15(a, b, c):
    try:
        result = (a ** 6 + b ** 7 + c ** 8) * math.acosh(a + b + c + 1)
        result += (a * b * c) ** (1/6) * math.atan(a + b + c)
        result *= math.exp(a / (b + c + 1))
        result = int(result)
        return result
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method16(a, b, c):
    try:
        result = (a ** 7 + b ** 8 + c ** 9) * math.asinh(a + b + c)
        result += (a * b * c) ** (1/7) * math.acos(a / (b + c + 1))
        result *= math.log(a + b + c + 1)
        result = int(result)
        return result
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method17(a, b, c):
    try:
        result = (a ** 8 + b ** 9 + c ** 10) * math.atanh(a + b + c)
        result += (a * b * c) ** (1/8) * math.sin(a + b + c)
        result *= math.exp(a / (b + c + 1))
        result = int(result)
        return result
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method18(a, b, c):
    try:
        result = (a ** 9 + b ** 10 + c ** 11) * math.cosh(a + b + c)
        result += (a * b * c) ** (1/9) * math.cos(a + b + c)
        result *= math.log(a + b + c + 1)
        result = int(result)
        return result
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method19(a, b, c):
    try:
        result = (a ** 10 + b ** 11 + c ** 12) * math.sinh(a + b + c)
        result += (a * b * c) ** (1/10) * math.tan(a + b + c)
        result *= math.exp(a / (b + c + 1))
        result = int(result)
        return result
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method20(a, b, c):
    try:
        result = (a ** 11 + b ** 12 + c ** 13) * math.tanh(a + b + c)
        result += (a * b * c) ** (1/11) * math.asin(a / (b + c + 1))
        result *= math.log(a + b + c + 1)
        result = int(result)
        return result
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method21(a, b, c):
    try:
        result = (a ** 2 + b ** 3 + c ** 4) / (math.log(a + 1) + math.log(b + 1) + math.log(c + 1))
        result = round(result)
        return max(result, a, b, c)
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method22(a, b, c):
    try:
        result = (a * b * c) ** (1/3) + math.sin(a) + math.cos(b) + math.tan(c)
        result = round(result)
        return max(result, a, b, c)
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method23(a, b, c):
    try:
        result = (a + b + c) * (math.exp(a) + math.exp(b) + math.exp(c))
        result = round(result)
        return max(result, a, b, c)
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method24(a, b, c):
    try:
        result = (a ** b + b ** c + c ** a) / (math.sqrt(a) + math.sqrt(b) + math.sqrt(c))
        result = round(result)
        return max(result, a, b, c)
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method25(a, b, c):
    try:
        result = (a * b * c) ** (1/3) + math.log(a + 1) + math.log(b + 1) + math.log(c + 1)
        result = round(result)
        return max(result, a, b, c)
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method26(a, b, c):
    try:
        result = (a + b + c) * (math.sin(a) + math.cos(b) + math.tan(c))
        result = round(result)
        return max(result, a, b, c)
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method27(a, b, c):
    try:
        result = (a ** 2 + b ** 3 + c ** 4) / (math.exp(a) + math.exp(b) + math.exp(c))
        result = round(result)
        return max(result, a, b, c)
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method28(a, b, c):
    try:
        result = (a * b * c) ** (1/3) + math.sqrt(a) + math.sqrt(b) + math.sqrt(c)
        result = round(result)
        return max(result, a, b, c)
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method29(a, b, c):
    try:
        result = (a + b + c) * (math.log(a + 1) + math.log(b + 1) + math.log(c + 1))
        result = round(result)
        return max(result, a, b, c)
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method30(a, b, c):
    try:
        result = (a ** b + b ** c + c ** a) / (math.sin(a) + math.cos(b) + math.tan(c))
        result = round(result)
        return max(result, a, b, c)
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method31(a, b, c):
    try:
        result = (a ** 3 + b ** 2 + c) * math.log(a + b + c + 1)
        result += (a * b * c) ** (1/3)
        result = math.ceil(result)
        return result
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method32(a, b, c):
    try:
        result = (a ** 2 + b ** 3 + c ** 4) * math.sin(a + b + c)
        result += (a + b + c) ** (1/5)
        result = math.ceil(result)
        return result
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method33(a, b, c):
    try:
        result = (a ** 4 + b ** 5 + c ** 6) * math.cos(a + b + c)
        result += (a * b * c) ** (1/7)
        result = math.ceil(result)
        return result
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method34(a, b, c):
    try:
        result = (a ** 5 + b ** 6 + c ** 7) * math.tan(a + b + c)
        result += (a + b + c) ** (1/9)
        result = math.ceil(result)
        return result
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method35(a, b, c):
    try:
        result = (a ** 6 + b ** 7 + c ** 8) * math.exp(a + b + c)
        result += (a * b * c) ** (1/11)
        result = math.ceil(result)
        return result
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method36(a, b, c):
    try:
        result = (a ** 7 + b ** 8 + c ** 9) * math.log10(a + b + c + 1)
        result += (a + b + c) ** (1/13)
        result = math.ceil(result)
        return result
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method37(a, b, c):
    try:
        result = (a ** 8 + b ** 9 + c ** 10) * math.sqrt(a + b + c)
        result += (a * b * c) ** (1/15)
        result = math.ceil(result)
        return result
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method38(a, b, c):
    try:
        result = (a ** 9 + b ** 10 + c ** 11) * math.asin(min(1, a / (a + b + c)))
        result += (a + b + c) ** (1/17)
        result = math.ceil(result)
        return result
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method39(a, b, c):
    try:
        result = (a ** 10 + b ** 11 + c ** 12) * math.acos(min(1, b / (a + b + c)))
        result += (a * b * c) ** (1/19)
        result = math.ceil(result)
        return result
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method40(a, b, c):
    try:
        result = (a ** 11 + b ** 12 + c ** 13) * math.atan(min(1, c / (a + b + c)))
        result += (a + b + c) ** (1/21)
        result = math.ceil(result)
        return result
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method41(a, b, c):
    try:
        result = (a ** 2 + b ** 3 + c ** 4) * math.sin(a + b + c) + math.log(a + b + c + 1)
        return round(result)
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method42(a, b, c):
    try:
        result = (a * b * c) ** (1/3) + math.exp(a + b + c) + math.cos(a * b * c)
        return round(result)
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method43(a, b, c):
    try:
        result = (a + b + c) ** (1/2) + math.tan(a + b + c) + math.log10(a + b + c + 1)
        return round(result)
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method44(a, b, c):
    try:
        result = (a ** b + b ** c + c ** a) * math.sinh(a + b + c) + math.sqrt(a + b + c)
        return round(result)
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method45(a, b, c):
    try:
        result = (a * b * c) ** (1/4) + math.atan(a + b + c) + math.exp(a * b * c)
        return round(result)
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method46(a, b, c):
    try:
        result = (a + b + c) ** (1/3) + math.asin(a / (a + b + c)) + math.log(a + b + c + 1)
        return round(result)
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method47(a, b, c):
    try:
        result = (a ** 3 + b ** 3 + c ** 3) * math.cosh(a + b + c) + math.sqrt(a + b + c)
        return round(result)
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method48(a, b, c):
    try:
        result = (a * b * c) ** (1/5) + math.acos(b / (a + b + c)) + math.exp(a + b + c)
        return round(result)
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method49(a, b, c):
    try:
        result = (a + b + c) ** (1/4) + math.atanh(c / (a + b + c)) + math.log10(a + b + c + 1)
        return round(result)
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)

def method50(a, b, c):
    try:
        result = (a ** 4 + b ** 4 + c ** 4) * math.sin(a + b + c) + math.sqrt(a + b + c)
        return round(result)
    except:
        stack = traceback.format_exc()
        trace = sys.exc_info()[2]
        raise HashError(stack, file = __name__, debug = DEBUG)
