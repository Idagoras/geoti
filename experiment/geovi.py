import perturbation
import perturbation as pb


def get_dp_start_and_destination_pair(points_in_start_buckets: list, points_in_end_buckets: list) -> list:
    dp_start = perturbation.perturbByExponentialMechanismWithGraph(points_in_start_buckets)
    dp_end = perturbation.perturbByExponentialMechanismWithGraph(points_in_end_buckets)
    return [dp_start, dp_end]
