def accepts(images):
    return (
        isinstance(images, Tuple)
        and len(images) > 0
        and all(image.is_Integer for image in images)
        and sorted(images) == list(range(len(images)))
    )


def compute(images):
    return Permutation([int(image) for image in images])
