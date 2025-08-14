aksub
=====

A generic ROS2 subscriber that can receive numbers, strings, images, or video frames with minimal setup.

Installation
------------
First, make sure you have a working ROS2 environment with `rclpy` and `cv_bridge` installed.

Then clone this repository and install:

    git clone https://github.com/yourname/aksub.git
    cd aksub
    pip install .

Usage
-----
Example Python usage:

    import aksub

    aksub.metadata(
        mode=None,           # Auto-detect from datatype
        datatype="Float64",  # e.g., "String", "Int32", "Image"
        node_name="num_subscriber",
        topic_name="number",
        queue=10,
        delay=1.0
    )

    print("Received value:", aksub.received_value)

Supported Datatypes
-------------------
- String (std_msgs.msg.String)
- Int32 (std_msgs.msg.Int32)
- Float32 (std_msgs.msg.Float32)
- Float64 (std_msgs.msg.Float64)
- Bool (std_msgs.msg.Bool)
- Image (sensor_msgs.msg.Image)

Accessing Received Data
-----------------------
- For String, Int, Float, Bool: `aksub.received_value` will be a Python primitive (str, int, float, bool).
- For Image/Video: `aksub.received_value` will be an OpenCV BGR image (numpy array).

Example for image:

    import cv2
    frame = aksub.received_value
    if frame is not None:
        cv2.imshow("Received Image", frame)
        cv2.waitKey(0)

Example for video stream:

    import cv2
    while True:
        frame = aksub.received_value
        if frame is not None:
            cv2.imshow("Video", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    cv2.destroyAllWindows()

Notes
-----
- `mode` can be "number", "string", "image", "video", or None for auto-detect.
- You can change `node_name`, `queue`, and `delay` in `metadata()`.
- `delay` can be used to control the processing interval.
- Requires `rclpy` and `cv_bridge` to be installed in your ROS2 Python environment.