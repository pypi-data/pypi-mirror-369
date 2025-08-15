from rich import print as rprint


def pinc(old, new):
    diff = new - old
    pdelta = (diff / old) * 100
    times_more = new/old
    return rprint(f"new: {new} | old: {old} \np_increase {pdelta:,.0f}% | {times_more:,.0f} times_more | diff: {diff:,.0f}" )

if __name__ == "__main__":
    # saginaw 0 -> 1 
    pinc(23_000, 13_000_000)
    pinc(13_000_000, 160_000_000)
    pinc(1_400_000, 3_700_000)