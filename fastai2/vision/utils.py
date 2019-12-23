# AUTOGENERATED! DO NOT EDIT! File to edit: dev/09b_vision.utils.ipynb (unless otherwise specified).

__all__ = ['download_images', 'resize_to', 'verify_image', 'verify_images']

# Cell
from ..torch_basics import *
from ..data.all import *
from .core import *

# Cell
def _download_image_inner(dest, inp, timeout=4):
    i,url = inp
    suffix = re.findall(r'\.\w+?(?=(?:\?|$))', url)
    suffix = suffix[0] if len(suffix)>0  else '.jpg'
    try: download_url(url, dest/f"{i:08d}{suffix}", overwrite=True, show_progress=False, timeout=timeout)
    except Exception as e: f"Couldn't download {url}."

# Cell
def download_images(url_file, dest, max_pics=1000, n_workers=8, timeout=4):
    "Download images listed in text file `url_file` to path `dest`, at most `max_pics`"
    urls = url_file.read().strip().split("\n")[:max_pics]
    dest = Path(dest)
    dest.mkdir(exist_ok=True)
    parallel(partial(_download_image_inner, dest, timeout=timeout), list(enumerate(urls)), n_workers=n_workers)

# Cell
def resize_to(img, targ_sz, use_min=False):
    "Size to resize to, to hit `targ_sz` at same aspect ratio, in PIL coords (i.e w*h)"
    w,h = img.size
    min_sz = (min if use_min else max)(w,h)
    ratio = targ_sz/min_sz
    return int(w*ratio),int(h*ratio)

# Cell
@delegates(Image.Image.save)
def verify_image(file, delete=True, max_size=None, dest=None, n_channels=3, interp=Image.BILINEAR, ext=None, img_format=None, resume=False, **kwargs):
    "Check if the image in `file` exists, maybe resize it and copy it in `dest`."
    try:
        # deal with partially broken images as indicated by PIL warnings
        with warnings.catch_warnings():
            warnings.filterwarnings('error')
            try: Image.open(file)
            except Warning as w:
                if "Possibly corrupt EXIF data" in str(w):
                    if delete: # green light to modify files
                        print(f"{file}: Removing corrupt EXIF data")
                        warnings.simplefilter("ignore")
                        PIL.Image.open(file).save(file)
                    else: print(f"{file}: Corrupt EXIF data, pass `delete=True` to remove it")
                else: warnings.warn(w)

        img = Image.open(file)
        imgarr = np.array(img)
        img_channels = 1 if len(imgarr.shape) == 2 else imgarr.shape[2]
        if (max_size is not None and (img.height > max_size or img.width > max_size)) or img_channels != n_channels:
            assert dest is not None, "You should provide `dest` Path to save resized image"
            dest_fname = Path(dest)/file.name
            if ext is not None: dest_fname=dest_fname.with_suffix(ext)
            if resume and os.path.isfile(dest_fname): return
            if max_size is not None:
                new_sz = resize_to(img, max_size)
                img = img.resize(new_sz, resample=interp)
            if n_channels == 3: img = img.convert("RGB")
            img.save(dest_fname, img_format, **kwargs)
    except Exception as e:
        print(f'{e}')
        if delete: file.unlink()

# Cell
@delegates(verify_image)
def verify_images(path, max_workers=4, recurse=False, dest='.', **kwargs):
    "Check if the images in `path` aren't broken, maybe resize them and copy it in `dest`."
    path = Path(path)
    dest = path/Path(dest)
    os.makedirs(dest, exist_ok=True)
    files = get_image_files(path, recurse=recurse)
    func = partial(verify_image, dest=dest, **kwargs)
    parallel(func, files, max_workers=max_workers)