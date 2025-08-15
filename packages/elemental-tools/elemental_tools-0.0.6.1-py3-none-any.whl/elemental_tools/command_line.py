# <h4>
# Remove Duplicate Images:
# </h4>
#
# ````
# img "/path/to/folder/with/duplicate/images"
# ````


# Remove duplicates
self.add_argument('-rd', '--remove_duplicates', default=None, action='store_true', help='Remove duplicate images')


def remove_duplicate_images(path):
    """
    Find and remove duplicate images in a folder.

    Parameters:
    - path (str): Path to the folder containing images.

    Returns:
    None
    """
    image_hashes = {}

    def calculate_image_hash(img_path):
        """
        Calculate the perceptual hash of an image.

        Parameters:
        - image_path (str): Path to the image file.

        Returns:
        - str: Perceptual hash of the image.
        """
        img = Image.open(img_path)
        hash_value = imagehash.phash(img)
        return str(hash_value)

    hash_value = calculate_image_hash(path)
    if hash_value in image_hashes:
        # Remove the duplicate image
        os.remove(path)
        print(f"Removed duplicate: {path}")
    else:
        # Store the hash for future comparisons
        image_hashes[hash_value] = path


def main():
    if args.remove_duplicates is not None:
        log("info", f"Checking for Duplicates...")
        remove_duplicate_images(args.input_path, args.duplicates)