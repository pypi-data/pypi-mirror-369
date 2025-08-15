import os
from typing import List, Optional

import oras.client
import requests

from .config import config


class ShipctlOrasClient(oras.client.OrasClient):
    """
    Custom ORAS client that handles shipctl-specific media types and manifest modifications.
    """

    def push(
        self,
        target: str,
        files: Optional[List] = None,
        config_path: Optional[str] = None,
        manifest_annotations: Optional[dict] = None,
        **kwargs,
    ) -> requests.Response:
        """
        Push shipctl artifacts with custom media types.
        """
        shipctl_files = []
        if files:
            for file_path in files:
                if ":" not in str(
                    file_path
                ):  # Only add media type if not already specified
                    shipctl_file = f"{file_path}:{config.ARTIFACT_CONTENT_MEDIA_TYPE}"
                    shipctl_files.append(shipctl_file)
                else:
                    shipctl_files.append(file_path)

        if not config_path:
            import json
            import tempfile

            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".json", delete=False
            ) as f:
                json.dump({}, f)
                config_path = f"{f.name}:{config.CONFIG_MEDIA_TYPE}"

        return self.push(
            target=target,
            files=shipctl_files,
            manifest_config=config_path,
            manifest_annotations=manifest_annotations,
            **kwargs,
        )

    def pull(
        self,
        target: str,
        config_path: Optional[str] = None,
        allowed_media_type: Optional[List] = None,
        overwrite: bool = True,
        outdir: Optional[str] = None,
    ) -> List[str]:
        """
        Override the default pull method to handle defined media types.
        """
        import oras.defaults
        import oras.utils
        from oras.logger import logger

        container = self.get_container(target)
        self.auth.load_configs(
            container, configs=[config_path] if config_path else None
        )
        manifest = self.get_manifest(container, allowed_media_type)
        outdir = outdir or oras.utils.get_tmpdir()

        files = []
        for layer in manifest.get("layers", []):
            filename = (layer.get("annotations") or {}).get(
                oras.defaults.annotation_title
            )
            if not filename:
                filename = layer["digest"]

            outfile = oras.utils.sanitize_path(outdir, os.path.join(outdir, filename))

            if not overwrite and os.path.exists(outfile):
                logger.warning(
                    f"{outfile} already exists and --keep-old-files set, will not overwrite."
                )
                continue

            media_type = layer["mediaType"]

            should_extract = (
                media_type == oras.defaults.default_blob_dir_media_type
                or media_type == config.ARTIFACT_CONTENT_MEDIA_TYPE
            )

            if should_extract:
                targz = oras.utils.get_tmpfile(suffix=".tar.gz")
                self.download_blob(container, layer["digest"], targz)
                oras.utils.extract_targz(targz, os.path.dirname(outfile))
                if os.path.exists(targz):
                    os.remove(targz)
            else:
                self.download_blob(container, layer["digest"], outfile)

            logger.info(f"Successfully pulled {outfile}.")
            files.append(outfile)
        return files
