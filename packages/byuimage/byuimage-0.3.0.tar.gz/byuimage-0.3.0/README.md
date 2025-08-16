# BYU Simple Image Library

This is a simple library for interacting with images. It is used for
instruction in an introductory programming class, *CS 110 Introduction to
Programming*, and *CS 111 Introduction to Computer Science* at Brigham Young University.

The interface for this library is based off a [similar library
developed at Stanford
University](https://web.stanford.edu/class/cs106a/handouts_w2021/reference-image.html),
but was developed independently.

## Importing the Library

```python
from byuimage import Image
```

## Creating an image

```python
image = Image(filename)
```

- creates a new image from a filename

```python
image = Image.blank(width, height)
```

- creates a new, blank, white image with the given width and height

## Image properties

```python
image.height
```

- returns image height in pixels

```python
image.width
```

- returns image width in pixels

## Iterating over pixels in an image

```python
for pixel in image:
```

- loops over all pixels, from left to right and top to bottom

```python
for y in range(image.height):
    for x in range(image.width):
```

- loops over all pixels, from left to right and top to bottom

## Getting and setting pixels

```python
pixel = image.get_pixel(x,y)
```

- gets the pixel at the given (x,y) coordinate

```python
pixel.red = value
pixel.green = value
pixel.blue = value
```

- Sets the pixel red, green, or blue value to the given value

```python
pixel.color = (10, 10, 10)

pixel.color = otherpixel.color
```

- Sets the pixel red, green, and blue values to the given tuple or pixel color

## Showing and saving images

```python
image.show()
```

- shows an image

```python
image.save(filename)
```

- saves an image


## Credits

The sample image used here is a photo from Mike Newbry, using the Unsplash
License, and is available for free at [https://unsplash.com/photos/BTE-k0V19Gw](https://unsplash.com/photos/BTE-k0V19Gw)

