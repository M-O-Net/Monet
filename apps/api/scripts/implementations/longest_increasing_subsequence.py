def accepts(p):
    return isinstance(p, Permutation)


def compute(p):
    images = p.array_form
    ending_at = []
    for image in images:
        shorter = [n for n, earlier in zip(ending_at, images, strict=False) if earlier < image]
        ending_at.append(1 + max(shorter, default=0))
    return max(ending_at)
