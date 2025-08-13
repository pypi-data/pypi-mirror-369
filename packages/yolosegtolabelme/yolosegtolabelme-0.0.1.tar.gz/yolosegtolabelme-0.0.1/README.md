# yoloseg2labelme

A python script for converting segmentation annotation from yolo-txt to labelme-json format.


## Installation
```bash
pip install yoloseg-to-labelme
```
## Usage
Arguments:

`--yolo` : path to YOLO annotations directory.

`--labelme(optional)` : path to output directory.
 
`--width(optional)` : default value is 1024.

`--height(optional)` : default value is 1024.

`--classes` : Path to the classes file(TXT format).

`--img_ext(optional)` : Default extension is "jpg".

### CLI Usage:
Specify yolo-labels-directory, output directory(optional), classes file, image size(width, height)(optional), and image extention(optional).

```bash
yolosegtolabelme --yolo path/to/yoloAnnotations --labelme path/to/output --classes path/to/classes-file
```

## Useful links

Yolo to labelme: https://pypi.org/project/yolo-to-labelme/

Lableme to yolo : https://pypi.org/project/labelme2yolo/
