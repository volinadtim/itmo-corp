#
# Complete the 'approximate_sigmoid' function below.
#
# The function is expected to return a DOUBLE.
# The function accepts following parameters:
#  1. DOUBLE_ARRAY x_axis
#  2. DOUBLE_ARRAY y_axis
#

def approximate_sigmoid(x_axis, y_axis):
    max_deviation = max(abs(y - 1 / (1 + math.exp(-x))) for x, y in zip(x_axis, y_axis))
    return max_deviation