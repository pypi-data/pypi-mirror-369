class BaseModelLoader:
    """Common base class for model loading and device management."""

    def __init__(
        self,
        model_path: str | None = None,
        model_bytes: bytes | None = None,
        device: str = "cuda",
    ) -> None:
        self.device = device
        self.model_path = model_path if model_path else ""
        self.model_bytes = model_bytes if model_bytes else None

        # Extract device_id from device string
        if "cpu" in device:
            self.device_id = "-1"
        elif "cuda:" in device or "trt:" in device:
            self.device_id = device.split(":")[-1]
        else:
            self.device_id = "0"
