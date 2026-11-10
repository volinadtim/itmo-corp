def first_deriative_1(args: []) -> float:
    return math.cos(args[0])


def first_deriative_2(args: []) -> float:
    return 1


def second_deriative_1(args: []) -> float:
    return args[1] / 2


def second_deriative_2(args: []) -> float:
    return args[0] / 2


def third_deriative_1(args: []) -> float:
    return (args[1] + k) / pow(math.cos(args[0] * args[1] + k), 2) - 2 * args[0]


def third_deriative_2(args: []) -> float:
    return (args[0] + k) / pow(math.cos(args[0] * args[1] + k), 2)


def fourth_deriative_1(args: []) -> float:
    return 2 * a * args[0]


def fourth_deriative_2(args: []) -> float:
    return 4 * args[1]


def fifth_deriative_1(args: []) -> float:
    return 2 * args[0]


def fifth_deriative_2(args: []) -> float:
    return 2 * args[1]


def fifth_deriative_3(args: []) -> float:
    return 2 * args[2]


def six_deriative_1(args: []) -> float:
    return 4 * args[0]


def six_deriative_2(args: []) -> float:
    return 2 * args[1]


def six_deriative_3(args: []) -> float:
    return -4


def seven_deriative_1(args: []) -> float:
    return 6 * args[0]


def seven_deriative_2(args: []) -> float:
    return -4


def seven_deriative_3(args: []) -> float:
    return 2 * args[2]


def jacobian(n: int, args: []):
    if n == 1:
        return [[first_deriative_1(args), first_deriative_2(args)],
                [second_deriative_1(args), second_deriative_2(args)]]
    elif n == 2 or n == 3:
        return [[third_deriative_1(args), third_deriative_2(args)],
                [fourth_deriative_1(args), fourth_deriative_2(args)]]
    elif n == 4:
        return [[fifth_deriative_1(args), fifth_deriative_2(args), fifth_deriative_3(args)],
                [six_deriative_1(args), six_deriative_2(args), six_deriative_3(args)],
                [seven_deriative_1(args), seven_deriative_2(args), seven_deriative_3(args)]]
    else:
        return [[default_function]]


def solve_by_fixed_point_iterations(system_id, number_of_unknowns, initial_approximations):
    if system_id > 4:
        return initial_approximations
    eps = 1e-5
    max_iter = 1000
    values = list(initial_approximations)
    funcs = get_functions(system_id)
    it = 0
    for _ in range(max_iter):
        try:
            f_vals = [funcs[i](values) for i in range(number_of_unknowns)]
        except ValueError:
            return values
        J = jacobian(system_id, values)
        J_inv = [[J[j][i] for j in range(len(J))] for i in range(len(J[0]))]
        delta = []
        for i in range(len(J)):
            s = sum(J_inv[i][k] * f_vals[k] for k in range(len(f_vals)))
            delta.append(-s)
        if all(abs(d) < eps for d in delta):
            return values
        for i in range(len(delta)):
            values[i] += delta[i]
    return values

