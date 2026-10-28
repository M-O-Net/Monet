def accepts(p):
    return isinstance(p, Permutation)


def compute(p):
    insertion, recording = [], []
    for step, value in enumerate(p.array_form, start=1):
        bumped = value + 1
        for row in range(len(insertion) + 1):
            if row == len(insertion):
                insertion.append([bumped])
                recording.append([step])
                break
            larger = [k for k, cell in enumerate(insertion[row]) if cell > bumped]
            if not larger:
                insertion[row].append(bumped)
                recording[row].append(step)
                break
            insertion[row][larger[0]], bumped = bumped, insertion[row][larger[0]]
    return Tableau(insertion), Tableau(recording)
