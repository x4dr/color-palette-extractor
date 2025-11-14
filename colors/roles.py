import colorsys
import itertools

import math
import numpy as np

from colors.Color import Color


def normalize(scores):
    min_val = min(scores)
    max_val = max(scores)
    if max_val == min_val:
        return [0.0] * len(scores)
    return [(s - min_val) / (max_val - min_val) for s in scores]


def hsv_distance_conical(hsv1, hsv2):
    h1, s1, v1 = hsv1
    h2, s2, v2 = hsv2
    h1_rad = h1 * 2 * math.pi
    h2_rad = h2 * 2 * math.pi
    x1 = s1 * math.cos(h1_rad)
    y1 = s1 * math.sin(h1_rad)
    z1 = v1
    x2 = s2 * math.cos(h2_rad)
    y2 = s2 * math.sin(h2_rad)
    z2 = v2
    return math.sqrt((x1 - x2) ** 2 + (y1 - y2) ** 2 + (z1 - z2) ** 2)


def score_dominant_cluster(cluster_sizes, idx):
    return cluster_sizes[idx]


def primaries(cluster_hsvs):
    def hue_distance(h1, h2):
        return min(abs(h1 - h2), 1 - abs(h1 - h2))  # h in 0..1

    def rgb_distance(rgb1, rgb2):
        max_dist = math.sqrt(255**2 * 3)
        return math.sqrt(sum((c1 - c2) ** 2 for c1, c2 in zip(rgb1, rgb2))) / max_dist

    def score_combo(combo):
        sats = [s for h, s, v in combo]
        vals = [v for h, s, v in combo]
        colors = [Color(*c) for c in combo]

        # distances
        hue_dist = sum(
            [
                hue_distance(colors[i].h, colors[(i + 1) % len(colors)].h)
                for i in range(len(colors))
            ]
        )
        rgb_dist = sum(
            [
                rgb_distance(colors[i].rgb, colors[(i + 1) % len(colors)].rgb)
                for i in range(len(colors))
            ]
        )

        # penalties
        gray_penalty = sum([(1 - s) ** 2 for s in sats])
        dark_penalty = sum([max(0, 0.2 - v) ** 2 for v in vals])

        # weighted sum
        score = (
            sum(sats) / len(sats) + 0.5 * hue_dist + 0.5 * rgb_dist - 0.5 * gray_penalty
        )  # - 0.3 * dark_penalty
        # debug
        # print(hue_dist, rgb_dist, gray_penalty, dark_penalty, score)
        return score

    best_combo = max(itertools.combinations(cluster_hsvs, 3), key=score_combo)
    return (Color(*x) for x in best_combo)


def score_neutral_cluster(cluster_hsvs, idx):
    return 1 - cluster_hsvs[idx][1]


def score_accent_cluster(cluster_hsvs, idx):
    return cluster_hsvs[idx][1]


def score_outlier_cluster(cluster_hsvs, idx):
    target = cluster_hsvs[idx]
    total_distance = 0
    for j, hsv in enumerate(cluster_hsvs):
        if j != idx:
            total_distance += hsv_distance_conical(target, hsv)
    return total_distance / (len(cluster_hsvs) - 1)


def score_highlight_cluster(cluster_hsvs, idx):
    return cluster_hsvs[idx][1] * cluster_hsvs[idx][2]


def score_shadow_cluster(cluster_hsvs, idx):
    return 1 - cluster_hsvs[idx][2]


def score_midtone_cluster(cluster_hsvs, idx):
    return 1 - abs(cluster_hsvs[idx][2] - 0.5)


def score_contrasting_cluster(cluster_hsvs, idx, dominant_idx):
    h0, _, v0 = cluster_hsvs[dominant_idx]
    hue_diff = min(abs(cluster_hsvs[idx][0] - h0), 1 - abs(cluster_hsvs[idx][0] - h0))
    value_diff = abs(cluster_hsvs[idx][2] - v0)
    return hue_diff + value_diff


def get_roles(image, kmeans, colors) -> dict[str, Color]:
    labels, counts = np.unique(kmeans.labels_, return_counts=True)
    cluster_centers = kmeans.cluster_centers_.astype(int)
    cluster_hsvs = np.array(
        [colorsys.rgb_to_hsv(*rgb / 255) for rgb in cluster_centers]
    )
    color_sizes = {Color(*cluster_hsvs[i]).hex: counts[i] for i in range(len(counts))}

    roles_to_colors = {}
    assigned = set()

    def penalize(s):
        return [s * 0.5 if i in assigned else s for i, s in enumerate(s)]

    # Dominant
    dominant_scores = normalize(
        [score_dominant_cluster(counts, i) for i in range(len(cluster_centers))]
    )
    dominant_idx = np.argmax(dominant_scores)
    assigned.add(dominant_idx)
    roles_to_colors["dominant"] = Color(*cluster_hsvs[dominant_idx])

    # Secondary
    secondary_idx = np.argsort(dominant_scores)[-2]
    assigned.add(secondary_idx)
    roles_to_colors["supporting"] = Color(*cluster_hsvs[secondary_idx])

    # Accent
    scores = penalize(
        normalize(
            [score_accent_cluster(cluster_hsvs, i) for i in range(len(cluster_centers))]
        )
    )
    idx = np.argmax(scores)
    assigned.add(idx)
    roles_to_colors["accent"] = Color(*cluster_hsvs[idx])

    # Neutral
    scores = penalize(
        normalize(
            [
                score_neutral_cluster(cluster_hsvs, i)
                for i in range(len(cluster_centers))
            ]
        )
    )
    idx = np.argmax(scores)
    assigned.add(idx)
    roles_to_colors["neutral"] = Color(*cluster_hsvs[idx])

    # Outlier
    scores = penalize(
        normalize(
            [
                score_outlier_cluster(cluster_hsvs, i)
                for i in range(len(cluster_centers))
            ]
        )
    )
    idx = np.argmax(scores)
    assigned.add(idx)
    roles_to_colors["outlier"] = Color(*cluster_hsvs[idx])

    # Highlight
    scores = penalize(
        normalize(
            [
                score_highlight_cluster(cluster_hsvs, i)
                for i in range(len(cluster_centers))
            ]
        )
    )
    idx = np.argmax(scores)
    assigned.add(idx)
    roles_to_colors["highlight"] = Color(*cluster_hsvs[idx])

    # Shadow
    scores = penalize(
        normalize(
            [score_shadow_cluster(cluster_hsvs, i) for i in range(len(cluster_centers))]
        )
    )
    idx = np.argmax(scores)
    assigned.add(idx)
    roles_to_colors["shadow"] = Color(*cluster_hsvs[idx])

    # Midtone
    scores = penalize(
        normalize(
            [
                score_midtone_cluster(cluster_hsvs, i)
                for i in range(len(cluster_centers))
            ]
        )
    )
    idx = np.argmax(scores)
    assigned.add(idx)
    roles_to_colors["midtone"] = Color(*cluster_hsvs[idx])

    # Contrasting
    scores = penalize(
        normalize(
            [
                score_contrasting_cluster(cluster_hsvs, i, dominant_idx)
                for i in range(len(cluster_centers))
            ]
        )
    )
    idx = np.argmax(scores)
    assigned.add(idx)
    roles_to_colors["contrasting"] = Color(*cluster_hsvs[idx])
    (
        roles_to_colors["primary"],
        roles_to_colors["secondary"],
        roles_to_colors["tertiary"],
    ) = sorted(primaries(cluster_hsvs), key=lambda x: color_sizes[x.hex], reverse=True)
    return roles_to_colors
