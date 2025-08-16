import math
from sympy import symbols, Eq, solve

def is_prime(n):
    if n <= 1:
        return False
    for i in range(2, int(math.sqrt(n)) + 1):
        if n % i == 0:
            return False
    return True

def is_lucky(n: int) -> bool:
    if n < 1:
        return False
    numbers = list(range(1, n * 2))
    idx = 1

    while idx < len(numbers):
        step = numbers[idx]
        if step == 0:
            break
        filtered = [num for i, num in enumerate(numbers) if (i + 1) % step != 0]
        numbers = filtered
        idx += 1

    return n in numbers

def is_lucky_prime(n: int) -> bool:
    return is_lucky(n) and is_prime(n)

def is_a_even(n):
    return n % 2 == 0

def is_an_odd(n):
    return n % 2 != 0

def is_positive(n):
    return n > 0

def is_negative(n):
    return n < 0

def is_zero(n):
    return n == 0

def is_square(n):
    if n < 0:
        return False
    root = int(math.sqrt(n))
    return root * root == n

def is_cube(n):
    if n < 0:
        root = round(abs(n) ** (1/3))
        return -root**3 == n
    root = round(n ** (1/3))
    return root ** 3 == n

def is_palindrome(n):
    s = str(abs(n))
    return s == s[::-1]

def is_perfect(n):
    if n <= 1:
        return False
    divisors = [i for i in range(1, n) if n % i == 0]
    return sum(divisors) == n

def is_fibonacci(n):
    return is_square(5*n*n + 4) or is_square(5*n*n - 4)

def is_harshad(n):
    digits = get_digits_of_number(n)
    return n % sum(digits) == 0

def is_monodigit(n):
    digits = get_digits_of_number(n)
    return all(d == digits[0] for d in digits)

def is_abundant(n: int) -> bool:
    if n < 1:
        return False
    divisors = [i for i in range(1, n) if n % i == 0]
    return sum(divisors) > n

def is_lasa(n: int) -> bool:
    if n < 1:
        return False
    divisors = [i for i in range(1, n) if n % i == 0]
    return sum(divisors) > 2 * n

def is_reel(n) -> bool:
    try:
        if n == float("inf") or n == float("-inf") or n != n:
            return False
        return isinstance(n, (int, float))
    except (TypeError, ValueError):
        return False

def digit_count(n):
    return len(str(abs(n)))

def mirror(n):
    s = str(abs(n))
    mirrored = int(s[::-1])
    return -mirrored if n < 0 else mirrored

def get_digits_of_number(n):
    return [int(digit) for digit in str(abs(n))]

def digit_frequency(n):
    from collections import Counter
    return dict(Counter(get_digits_of_number(n)))

def solve_equation(equation_str):
    x = symbols('x')
    try:
        lhs, rhs = equation_str.split('=')
        equation = Eq(eval(lhs), eval(rhs))
        return solve(equation, x)
    except Exception as e:
        return f"Error! Equation could not be solved: '{e}'"

def orbit(f, x0, steps=10):
    result = [x0]
    for _ in range(steps):
        x0 = f(x0)
        result.append(x0)
    return result

irrational_numbers = {
    "pi": math.pi,
    "tau": math.tau,
    "sin_1": math.sin(1),
    "ln_2": math.log(2),
    "squareroot_2": math.sqrt(2),
    "gold_ratio": (1 + math.sqrt(5)) / 2,
    "e": math.e
}