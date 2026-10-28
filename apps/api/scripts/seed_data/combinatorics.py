from seed_data.build import Instance, instance

INSTANCES: dict[str, Instance] = {
    "transposition": instance(r"\left( 0\; 1\right)", {"perm": [1, 0]}, ["Permutations"]),
    "swap_last": instance(r"\left( 1\; 2\right)", {"perm": [0, 2, 1]}, ["Permutations"]),
    "four_cycle": instance(
        r"\left( 0\; 1\; 2\; 3\right)", {"perm": [1, 2, 3, 0]}, ["Permutations"]
    ),
    "three_cycle": instance(r"\left( 0\; 1\; 2\right)", {"perm": [1, 2, 0]}, ["EvenPermutations"]),
    "three_cycle_inverse": instance(
        r"\left( 0\; 2\; 1\right)", {"perm": [2, 0, 1]}, ["EvenPermutations"]
    ),
    "double_transposition": instance(
        r"\left( 0\; 1\right)\left( 2\; 3\right)",
        {"perm": [1, 0, 3, 2]},
        ["EvenPermutations"],
    ),
    "partition_22": instance(
        r"\left(2, 2\right) \vdash 4", {"partition": [2, 2]}, ["IntegerPartitions"]
    ),
    "partition_311": instance(
        r"\left(3, 1, 1\right) \vdash 5", {"partition": [3, 1, 1]}, ["IntegerPartitions"]
    ),
    "partition_2211": instance(
        r"\left(2, 2, 1, 1\right) \vdash 6", {"partition": [2, 2, 1, 1]}, ["IntegerPartitions"]
    ),
    "partition_321": instance(
        r"\left(3, 2, 1\right) \vdash 6",
        {"partition": [3, 2, 1]},
        ["DistinctPartitions"],
        "The staircase partition.",
    ),
    "partition_41": instance(
        r"\left(4, 1\right) \vdash 5", {"partition": [4, 1]}, ["DistinctPartitions"]
    ),
    "partition_5": instance(r"\left(5\right) \vdash 5", {"partition": [5]}, ["DistinctPartitions"]),
    "tableau_32": instance(
        r"\begin{array}{lll}1 & 2 & 3 \\ 4 & 5\end{array}",
        {"tableau": [[1, 2, 3], [4, 5]]},
        ["StandardYoungTableaux"],
    ),
    "tableau_32_columns": instance(
        r"\begin{array}{lll}1 & 3 & 5 \\ 2 & 4\end{array}",
        {"tableau": [[1, 3, 5], [2, 4]]},
        ["StandardYoungTableaux"],
    ),
    "tableau_211": instance(
        r"\begin{array}{ll}1 & 2 \\ 3 \\ 4\end{array}",
        {"tableau": [[1, 2], [3], [4]]},
        ["StandardYoungTableaux"],
    ),
}
