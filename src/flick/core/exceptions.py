

class CreateDockerClientFailed(Exception):

    def __init__(self, reason) -> None:
        super().__init__(f"create docker client failed: {reason}")
