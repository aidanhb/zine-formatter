# RC Zine Formatter!

Custom zine formatter for the [RC Zine](https://zine.recurse.com). Given a folder of content images, this script generates a PDF layout for printing and individual PNGs for each page of content. Each content page is sized to a quarter sheet of A4 printer paper with the appropriate page number and image title in the footer, as well as the image content scaled to the body of the page.

## Setup

This project relies on Pillow and Python3. Navigate to the `zine-formatter` directory and run:
```
$ pip3 install requirements.txt
```

## Example:

Given a folder of input images:

![](assets/demo_image1.png)

Running the following code:
```
$ python3 format_pages.py -i my_images -o my_output -f volume3_pg{}.png
```
Will generate the following files in `my_output`:

<img src="assets/demo_image2.png" width="60%">

<img src="assets/demo_image3.png" width="60%">