"""Image 32 (community page 15): the 4 x 4 number table read as a spiral from the highlighted 3299 gives primes whose zero-based indices are Fibonacci numbers."""
GRID = [[3258, 3222, 3152, 3038], [3278, 3299, 3298, 2838], [3288, 3294, 3296, 2472], [4516, 1206, 708, 1820]]


def spiral(grid, start):
    r, c = start
    pos, dirs, step, d = [(r, c)], [(0, 1), (1, 0), (0, -1), (-1, 0)], 1, 0
    while len(pos) < 16:
        for _ in range(2):
            dr, dc = dirs[d % 4]
            for _ in range(step):
                r, c = r + dr, c + dc
                if 0 <= r < 4 and 0 <= c < 4:
                    pos.append((r, c))
            d += 1
        step += 1
    return [grid[r][c] for r, c in pos[:16]]


def test_spiral_gives_fibonacci_prime_indices():
    primes = [n for n in range(2, 8000) if all(n % q for q in range(2, int(n ** 0.5) + 1))]
    index = {p: i for i, p in enumerate(primes)}
    entries = spiral(GRID, (1, 1))
    assert entries[0] == 3299
    ids = [index[3301 - e if i < 14 else 3301 + e] for i, e in enumerate(entries)]
    assert ids == [0, 1, 2, 3, 5, 8, 13, 21, 34, 55, 89, 144, 233, 377, 610, 987]
