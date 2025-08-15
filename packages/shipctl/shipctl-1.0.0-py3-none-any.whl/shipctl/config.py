from dotenv import load_dotenv

load_dotenv()
import os


class AppConfig:
    def __init__(self):
        self.ARTIFACT_CONTENT_MEDIA_TYPE = os.environ.get(
            "SHIPCTL_ARTIFACT_CONTENT_MEDIA_TYPE",
            "application/vnd.shipctl.artifact.content.v1.tar+gzip",
        )
        self.CONFIG_MEDIA_TYPE = os.environ.get(
            "SHIPCTL_CONFIG_MEDIA_TYPE", "application/vnd.shipctl.config.v1+json"
        )


config = AppConfig()
