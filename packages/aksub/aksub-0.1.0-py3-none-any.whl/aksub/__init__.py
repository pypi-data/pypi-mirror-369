from .subscriber import run_subscriber, received_value

_config = {}

# This is the variable you'll read from outside
received_value = None

def metadata(
    mode=None,
    datatype="Float64",
    node_name="num_subscriber",
    topic_name="number",
    queue=10,
    delay=1.0
):
    """
    Set up and start the generic ROS2 subscriber.

    Example:
        import aksub
        aksub.metadata(datatype="String", topic_name="chatter")
        print(aksub.received_value)
    """
    global _config
    _config.update(locals())
    run_subscriber(**_config)
