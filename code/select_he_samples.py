import random, json
from pathlib import Path


def load_image_hashes(folder_path: Path, blacklist=[]):
    image_hashes = []
    for file in folder_path.iterdir():
        if not file.is_file() or file.stem in blacklist:
            continue
        dhash = file.stem
        image_hashes.append((dhash, file))
    return image_hashes


def hamming_distance(hash1, hash2):
    return bin(int(hash1, 16) ^ int(hash2, 16)).count("1")


def sample_diverse_images_greedy(image_hashes, similarity_threshold):
    sampled_images = []
    for dhash, image_path in image_hashes:
        is_diverse = True
        for sampled_dhash, _ in sampled_images:
            if hamming_distance(dhash, sampled_dhash) < similarity_threshold:
                is_diverse = False
                break
        if is_diverse:
            sampled_images.append((dhash, image_path))
    return sampled_images


def search_threshold(image_hashes, num_samples, sample_fn=sample_diverse_images_greedy):
    threshold = 0
    samples = []

    # not great complexity but probably never even runs up to 64/2.
    for sim in range(1, 64):
        sim_samples = sample_fn(image_hashes, sim)
        if len(sim_samples) >= num_samples:
            samples = sim_samples
            threshold = sim
            continue
        break

    return threshold, samples


if __name__ == "__main__":
    folder_path = Path("../outputs/icons/")
    output_file = Path("../outputs/k-shot-he-targets.json")
    num_samples = 60
    random.seed(42)
    blacklist = [
        # not icons
        "70b2694dd4862b45","072b96d44c69b270","71ccb25a732bb6b6","71d4949636229c94",
        "238c136969695571","238c176369694571","d4da9b9ad89ada94","d4c4d4d416969696",
        "d4c4d4d4d4d4d4d4","d4d4d4d4d4961696","9595959595919595","5484c4d417969696",
        "4941c96d4b4bc149","0101159515350101","49c1c9e9cb4b4149","0101959595950101",
        # training set for k-shot
        "f0d496d6d4d299aa","a2a9caa6d4d2ac11","6b94cc6719ae5384","4110f21333961084",
        "24806c5754688028","249038ec80c400a0","5826a2b8a702a500","694dd4e8a2d46869",
        "006080c1f0dc2cd5","9000d4d4dccc00c4","26d9d8d6d6d8d926","0c73e00e31c66491",
        "2bd45454d5d5d4e8","0278d4c2c6d49804","d8d4c6d6d4d8cce4","48a060caca60a048",
        "8811d2c629d8c849","b2694cf0f0557032","66d6bae2e2aae266","20d0c8a8c8ecbc34"
    ]

    all_image_hashes = load_image_hashes(folder_path, blacklist)
    random.shuffle(all_image_hashes)

    best_threshold, sampled_images = search_threshold(all_image_hashes, num_samples)
    sample_ids = [image_path.stem for _, image_path in sampled_images]

    print(f"Optimal similarity threshold: {best_threshold}")
    print(f"Threshold yields {len(sampled_images)} images.")

    if len(sampled_images) > num_samples:
        print(f"Shuffling and truncating to {num_samples} of samples.")
        random.shuffle(sampled_images)
        sampled_images = sampled_images[:num_samples]
        sample_ids = sample_ids[:num_samples]

    with output_file.open("w") as f:
        json.dump(sample_ids, f)
    print(f"Saved ids to {output_file}.")
