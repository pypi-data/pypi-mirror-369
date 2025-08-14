# Universal Publisher for ROS2

A flexible ROS2 publisher for **text, numbers, booleans, images, videos, and multi-float arrays**.

## Install
```bash
pip install universal-publisher

# Use
from unipub import unipub

unipub(
    mode="number",
    data_type="float",
    nodename="universal_publisher",
    topic_name="my_topic",
    queue_size=10,
    delay_period=0.033
)
