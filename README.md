# The assignment

You must make a python program which is able to detect faces and deem them an _Enemy_, _Friend_ or _Unknown_. If they're an _Enemy_, the drone must follow their face and face their direction. The interface will go through LabView which should be able to access all the drone's functions.

Because LabView is a 32-bit program, we've had to adapt and use the 32-bit version of python.

## pre-requisites

* Python 3.10.0 (32-bit)
* Tello Drone
* [OpenCV-python](https://pypi.org/project/opencv-python/)
* [DJITelloPy2](https://pypi.org/project/djitellopy2/)

## Getting started

Installing OpenCV and DJITelloPy is done via opening your terminal (powershell, etc) and executing the below command.

```python
pip install opencv-python djitellopy2
```

## Contributors

Though not directly involved in the development of the drone face-detection, they have contributed considerably in other fields of the assignemnt.

* [Eric T.](https://github.com/Eriomas), LabView Expert.
* [Thijs M.](https://github.com/TopdevT), Documentation management and code support.
