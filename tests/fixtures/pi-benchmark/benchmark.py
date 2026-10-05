"""A deliberately invalid speedup claim: only baseline performs the work."""
import time


def baseline(rows):
    return [str(row).encode() for row in rows]


def candidate(rows):
    return (str(row).encode() for row in rows)


if __name__ == '__main__':
    rows = list(range(100_000))
    for name, implementation in [('baseline', baseline), ('candidate', candidate)]:
        start = time.perf_counter()
        result = implementation(rows)
        # Neither outputs nor errors are checked. One sample per side.
        print(name, time.perf_counter() - start)
