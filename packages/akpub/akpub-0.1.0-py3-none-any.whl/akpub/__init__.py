from .publisher import run_publisher

_config = {}

def metadata(
    mode=None,
    datatype="Float64",
    node_name="num_publisher",
    topic_name="number",
    value=42.5,
    queue=10,
    delay=1.0,
    video_source=None
):
    """
    Set up and start the generic ROS2 publisher.

    Example:
        import akpub
        akpub.metadata(datatype="String", value="Hello ROS2")
    """
    global _config
    _config.update(locals())
    run_publisher(**_config)
