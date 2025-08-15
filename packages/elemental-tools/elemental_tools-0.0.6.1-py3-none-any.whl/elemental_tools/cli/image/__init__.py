import os
from typing import Union

from PIL import Image
from icecream import ic

from elemental_tools.cli.kernel import CLI, ArgumentParser
from elemental_tools.cli.parsers import parse_resolution, parse_mb
from elemental_tools.logger import Logger

log = Logger(app_name="Elemental-Tools", owner="img").log
supported_formats = ['.png', '.jpg', '.bmp', '.webp', '.gif', '.tiff', '.tif', '.jp2']
Image.MAX_IMAGE_PIXELS = 9331200000


class Render:
    debug: bool = False
    supress_log = False
    has_changed: bool = False

    input_path: str
    output_path: str
    img: Image.Image
    fmt = None

    optimize: bool = False
    quality = 100
    scale: int = 100
    min_scale: int = 1

    min_resolution: Union[tuple[int, int], None] = None
    resolution: Union[tuple[int, int], None] = None

    scale_step: int = 1

    width, height = (0, 0)

    _default_not_found_msg = "Failed to load image, probably no file found. Attempting to retrieve the image from buffer..."

    def __init__(self, img, input_path: str, output_path: str, min_resolution: tuple = None, resolution: tuple[int, int] = None, fmt=None,
                 optimize: bool = False,
                 supress_log: bool = False):
        self.img = img

        self.input_path = input_path
        self.output_path = output_path

        self.fmt = fmt
        self.optimize = optimize
        self.supress_log = supress_log

        self.width, self.height = self.img.size

        self.min_resolution = min_resolution
        self.resolution: Union[tuple[int, int], None] = resolution

        if self.fmt is not None:
            self.has_changed = True

    def run(self):
        self.width, self.height = self.img.size

        if self.resolution is not None:
            if any([self.width != self.resolution[0], self.height != self.resolution[1]]):
                self.img.resize(self.resolution)

        if self.debug:
            log("info", f"Rendering: {str(self.__dict__)}", origin="render")

        log("info", f"Saving Image File: {self.output_path}", supress=self.supress_log, origin="render")

        if not any([self.output_path.lower().endswith(fmt) for fmt in supported_formats]):

            self.output_path = os.path.join(self.output_path, os.path.basename(self.input_path))

        if self.fmt is None:
            os.makedirs(os.path.dirname(self.output_path), exist_ok=True)
            self.img.save(self.output_path, optimize=self.optimize, quality=int(self.quality), compression_level=0)

        else:
            # Conversion
            log("info", f"Converting from {str(os.path.basename(self.input_path))} to {self.fmt}", supress=self.supress_log, origin="render")
            output_path = f"{os.path.splitext(self.output_path)[0]}.{self.fmt}"
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            self.img.save(output_path, optimize=self.optimize, quality=int(self.quality), format=self.fmt, compression_level=0)

        log("success", f"Image Saved Successfully", supress=self.supress_log, origin="render")
        self.supress_log = False

        return self.output_path

    def reload_img(self):
        try:
            return Image.open(self.input_path)
        except:
            log("alert", self._default_not_found_msg, origin="render")
            return self.img

    def reload_img_from_render(self):
        try:
            self.img = Image.open(self.output_path)
            return self.img
        except:
            log("alert", self._default_not_found_msg, origin="render")
            return self.img

    def rescale(self, scale):
        self.width, self.height = self.img.size

        # Calculate the new resolutions
        new_width = int(self.width * scale / 100)
        new_height = int(self.height * scale / 100)

        # Resize the image
        if self.min_resolution:

            min_width = int(self.min_resolution[0])
            min_height = int(self.min_resolution[1])

            if not new_width > min_width and new_height > min_height:
                return self.img

        self.img = self.img.resize((new_width, new_height))

        return self.img

    def get_file_size(self):
        if self.output_path is not None:
            return os.path.getsize(self.output_path)

        return os.path.getsize(self.input_path)

    def adaptive_size(self, _target_size, increase: bool = False):

        def get_byte_size():
            actual_size_b_len = len(self.img.tobytes())
            actual_size_on_disk = os.path.getsize(self.input_path)

            actual_byte_size_ratio = actual_size_b_len / actual_size_on_disk

            return actual_byte_size_ratio

        def get_size_on_disk():
            return os.path.getsize(self.input_path)

        if not increase:
            while os.path.getsize(self.input_path) > _target_size:

                self.supress_log = True

                # Ridiculous rule of three c===3
                _target_size_in_bytes = _target_size * get_byte_size()
                _last_applied_scale = False

                # Find out how is the matching scale for the desired size
                # Other rule of three here to get the necessary scale according to the current file size
                size_on_disk_for_scale_percentage = get_size_on_disk() / 100

                target_scale = _target_size / size_on_disk_for_scale_percentage
                adaptive_scale = 100

                while len(self.img.tobytes()) >= int(_target_size_in_bytes):

                    _last_applied_scale = adaptive_scale
                    self.rescale(adaptive_scale)
                    
                    adaptive_scale -= self.scale_step

                    # Check if scaling twice
                    if max([self.min_scale, adaptive_scale]) == _last_applied_scale:
                        adaptive_scale -= self.scale_step
                        break

                self.run()
                self.reload_img()

        elif increase:
            while os.path.getsize(self.input_path) < _target_size:

                self.supress_log = True

                _target_size_in_bytes = _target_size * get_byte_size()
                _last_applied_scale = False

                while len(self.img.tobytes()) < _target_size_in_bytes:

                    size_on_disk_for_scale_percentage = get_size_on_disk() / 100

                    target_scale = int(_target_size / size_on_disk_for_scale_percentage)
                    adaptive_scale = target_scale

                    if self.debug:
                        log('info', f'Shrinking to scale {adaptive_scale}%', origin="adaptive-size")

                    _last_applied_scale = adaptive_scale
                    self.rescale(adaptive_scale)
                    adaptive_scale += self.scale_step
                    
                    # Check if scaling twice
                    if max([self.min_scale, adaptive_scale]) == _last_applied_scale:
                        adaptive_scale += self.scale_step
                        break

                self.run()
                self.reload_img()

        return self.output_path

    def set_has_change(self, state: bool = True):
        self.has_changed = state
        return self.has_changed


# >>> Arguments and functionality >>>
class Compression(ArgumentParser):
    lowest_quality = 5
    quality_step = 10

    class Errors:

        def unable_to_compress(self, path, bypass: bool = False):
            if not bypass:
                os.system('cls' if os.name == 'nt' else 'clear')
                overwrite = input(
                    "The desired file size could not be achieved with the parameters set. Please check our doc for more information.\nType YES and hit enter to proceed.\nHit CTRL + C or CMD + C to skip execution.\n")
                if not overwrite == "YES":
                    self.unable_to_compress(path)
                else:

                    return True

    def __init__(self):
        super().__init__()

        # Quality
        self.add_argument('--quality', '-q', default=100, help='Set the quality to the output image', type=int)

        # Minimum Size
        self.add_argument('--minimum_size', '-m', default=100, help='Set the quality to the output image',
                                 type=int)

        # Minimum Scale
        self.add_argument('--min_scale', type=int, default=Render.min_scale,
                                 help=f'The scale (percentage) that can be applied in order to compress the file to a target size')

        # Minimum resolution
        self.add_argument('--min_resolution', type=str, default=None,
                                 help=f'The limit of the resolution that can be applied while compressing the file to a target size')

        # Compression
        self.add_argument( '--max_file_size',
                                 help='The maximum file size for each image. Accepts either a size in megabytes (e.g., "1.5MB") or bytes (e.g., "1500000")')

        self.add_argument('--min_file_size',
                                 help='The minimum file size for each image. Accepts either a size in megabytes (e.g., "1.5MB") or bytes (e.g., "1500000")')

    def run(self, render: Render, args):
        _min_size = None

        if args.min_file_size is not None and args.max_file_size is not None:
            _min_size = parse_mb(args.min_file_size)
            _max_size = parse_mb(args.max_file_size)
            if _min_size > _max_size:
                raise Exception('You must be kidding... Your --min_file_size cannot exceed your --max_file_size.')

        # Compress
        if args.min_file_size is not None:
            _min_size = parse_mb(args.min_file_size)
            if render.get_file_size() < _min_size:
                log("info", f"Expanding file till it reach the minimum file size",
                    origin="compressor")

                render.min_scale = args.min_scale

                compressed_file_path = render.adaptive_size(_min_size, increase=True)

                last_retrieved_size = -1

                while os.path.getsize(compressed_file_path) < _min_size:
                    render.reload_img_from_render()
                    render.quality += self.quality_step
                    render.supress_log = True
                    render.run()

                    if os.path.getsize(compressed_file_path) == last_retrieved_size:
                        self.Errors().unable_to_compress(compressed_file_path, args.yes)
                        break

                    last_retrieved_size = os.path.getsize(compressed_file_path)

                if compressed_file_path is not None:
                    log("success", f"Expanded!",
                        origin="compressor")
                    render.set_has_change()
                else:
                    log("error", f"Failed to Expand", origin="compressor")
            else:
                log("info", f"Skipping shrinking file, since it's size is not bellow your choice.", origin="compressor")

        if args.max_file_size is not None:
            log("info", f"Compressing...", origin="compressor")

            _max_size = parse_mb(args.max_file_size)

            try:
                if os.path.getsize(render.input_path) < _max_size:
                    if _min_size is None:
                       log("alert", f"The provided size, exceeds the file size. Compression skipped.", origin="compressor")
                else:
                    render.min_scale = args.min_scale

                    compressed_file_path = render.adaptive_size(_max_size)
                    last_retrieved_size = -1

                    while os.path.getsize(compressed_file_path) > _max_size and args.quality > self.lowest_quality:
                        render.reload_img_from_render()
                        render.quality -= self.quality_step
                        render.supress_log = True
                        render.run()

                        if os.path.getsize(compressed_file_path) == last_retrieved_size:
                            self.Errors().unable_to_compress(compressed_file_path, args.yes)
                            break

                        last_retrieved_size = os.path.getsize(compressed_file_path)

                    if compressed_file_path is not None:
                        render.set_has_change()
                        log("success", f"Compressed!", origin="compressor")

                    else:
                        log("error", f"Failed to Compress", origin="compressor")

            except Exception as e:
                log("error", f"Failed to compress because of exception: {str(e)}", origin="compressor")
                return False

        return render.img


class Size(ArgumentParser):
    img = None
    args = None

    def_crop: int = 0
    def_min_scale: int = 1
    scale: int = 100

    resolution: Union[tuple[int, int], None] = None

    def __init__(self):
        super().__init__()

        # Crop
        self.add_argument('--crop_top', type=int, default=self.def_crop,
                                 help=f'Number of pixels to remove from the top (default: {str(self.def_crop)})')
        self.add_argument('--crop_bottom', type=int, default=self.def_crop,
                                 help=f'Number of pixels to remove from the bottom (default: {str(self.def_crop)})')
        self.add_argument('--crop_left', type=int, default=self.def_crop,
                                 help=f'Number of pixels to remove from the left (default: {str(self.def_crop)})')
        self.add_argument('--crop_right', type=int, default=self.def_crop,
                                 help=f'Number of pixels to remove from the right (default: {str(self.def_crop)})')

        # Resize
        self.add_argument('--scale', '-s', type=int, default=self.scale,
                                 help=f'The scale (percentage) you want to apply')
        self.add_argument('--resolution', '--dimension', type=str, default=None,
                                 help=f'The size in pixels like: 1920x1080')

    def resize_image_by_scale(self):
        self.scale = int(self.args.scale)

        if not self.scale == 100:
            log('info', f"Scaling image to: {str(self.scale)}%", origin="scale")

            # Get the original resolutions
            width, height = self.img.size

            # Calculate the new resolutions
            new_width = int(width * self.scale / 100)
            new_height = int(height * self.scale / 100)

            # Resize the image
            self.img = self.img.resize((new_width, new_height))
            log('success', f"Scaled!", origin="scale")

            return self.img

    def resize_image_by_resolution(self):
        if self.args.resolution is not None:

            self.resolution = parse_resolution(self.args.resolution)
            log('info', f"Setting Resolution: {str(self.resolution).replace('(', '').replace(')', '').replace(', ', 'X')}", origin="Resolution")
            self.img = self.img.resize((self.resolution[0], self.resolution[1]))
            log('success', f"Resized!", origin="Resolution")

            return self.img

    def crop_image(self):
        if any([self.args.__getattribute__(arg) for arg in self.args.__dict__ if "crop" in arg]):
            log("info",
                f"Cropping: \n\tTop: {self.args.crop_top} px\n\tBottom: {self.args.crop_bottom} px\n\tLeft: {self.args.crop_left} px\n\tRight: {self.args.crop_right} px", origin="crop")
            crop_left = self.args.crop_left
            crop_right = self.args.crop_right
            crop_top = self.args.crop_top
            crop_bottom = self.args.crop_bottom

            # Get image resolutions
            width, height = self.img.size

            # Crop the image
            self.img = self.img.crop((crop_left, crop_top, width - crop_right, height - crop_bottom))

            log("success",
                f"Cropped!", origin="crop")

            return self.img

    def run(self, render: Render, args):
        self.img = render.img
        self.args = args

        if any([
            self.crop_image() is not None,
            self.resize_image_by_scale() is not None,
            self.resize_image_by_resolution() is not None
        ]):
            render.set_has_change()

        return self.img


class Conversion(ArgumentParser):

    def __init__(self):
        super().__init__()
        self.add_argument('--output_format', '-fmt', choices=[e.replace(".", "") for e in supported_formats],
            help='Output image format')


# >>> CLI Declaration >>>
class ImageCLI(CLI):
    supported_formats = supported_formats

    compression = Compression()
    size = Size()
    conversion = Conversion()

    parser = ArgumentParser()
    parser.include_options(compression, conversion, size)

    dst = None
    user_path = ""

    _min_resolution_tuple: Union[tuple[int, int], None] = None
    _resolution_tuple: Union[tuple[int, int], None] = None

    def __init__(self):
        super().__init__()
        self.process_arguments()

    def run(self, filename, destination):

        if destination is not None:
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            self.args.output_path = destination
        else:
            self.args.output_path = filename

        # Open Image
        try:
            log("info", f"Opening Image: {filename}", origin='img')
            img = Image.open(filename)
            self.not_found = False

        except Exception as e:
            log("error", f"Failed to open!\n{str(e)}", origin='img')
            return False

        # Load the modifier min_resolution and parse the arg
        if self.args.min_resolution is not None:
            try:
                self._min_resolution_tuple = parse_resolution(self.args.min_resolution)
            except:
                raise Exception("Not a valid --min_resolution")

        # Initialize Render Module:
        render = Render(img, input_path=str(filename), output_path=self.args.output_path,
                        fmt=self.args.output_format, min_resolution=self._min_resolution_tuple)
        render.debug = self.args.debug

        if self.args.quality != 100:
            render.optimize = True

        # Apply Size:
        render.img = self.size.run(render, self.args)

        # Compress:
        render.img = self.compression.run(render, self.args)

        # Convert:
        render.fmt = self.args.output_format

        # Save:
        if render.has_changed:
            render.run()
        else:
            log("alert", f"Image skipped no changes to apply", origin='img')

        return True

