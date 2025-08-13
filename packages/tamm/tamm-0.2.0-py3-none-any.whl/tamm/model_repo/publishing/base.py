import abc
import tempfile
from pathlib import Path
from typing import Any, Optional, Union

import tamm.utils.json as tamm_json
from tamm.layers import ModuleConfig
from tamm.model_repo.publishing.config import PublishedModelConfig


class ModelPublisher(abc.ABC):
    def publish(
        self,
        payload: Union[Path, ModuleConfig, PublishedModelConfig],
        model_id: Optional[str] = None,
        project_id: Optional[str] = None,
        version_id: Optional[str] = None,
    ):
        """
        Publishes one of the following to a model repository

        1) A :class:`PublishedModelConfig`
        2) A :class:`ModuleConfig`
        3) A model config file path in :class:`pathlib.Path` or :obj:`str`
        4) Contents of ``directory`` (:class:`Path`, or :obj:`str`) which includes a
           config file (*.json) and ckpts

        Args:
            payload: :obj:`str`, :class:`Path`, :class:`ModuleConfig` or
                     :class:`PublishedModelConfig`
            model_id: Model ID override name of the model
                          (required if ``payload`` is not :class:`PublishedModelConfig`)
            project_id: Optional project ID for supported backends
            version_id: Optional version ID for supported backends

        Returns: A handle of the published model


        """
        if isinstance(payload, PublishedModelConfig):
            return self.publish_published_model_config(payload)
        if isinstance(payload, ModuleConfig):
            return self.publish_model_config(payload, model_id, project_id, version_id)
        if isinstance(payload, (str, Path)) and Path(payload).is_dir():
            return self.publish_directory(
                Path(payload), model_id, project_id, version_id
            )
        if isinstance(payload, (str, Path)) and Path(payload).is_file():
            return self.publish_file(Path(payload), model_id, project_id, version_id)

        raise ValueError(
            f"Cannot publish '{payload}' because it is not a recognized object. "
            f"Currently supports "
            f"1) PublishedModelConfig, "
            f"2) ModuleConfig, "
            f"3) A path to config.json, and "
            f"4) A directory path containing config.json and checkpoints"
        )

    def publish_published_model_config(
        self,
        published_model_config: "PublishedModelConfig",
        model_id: Optional[str] = None,
        project_id: Optional[str] = None,
        version_id: Optional[str] = None,
    ) -> Any:
        published_model_config = self._maybe_update_model_id(
            published_model_config, model_id, project_id, version_id
        )
        if not bool(published_model_config.model_id):
            raise ValueError(
                f"published_model_config.model_id must be a valid string, "
                f"got {published_model_config.model_id}"
            )
        with tempfile.TemporaryDirectory() as tmp_dir:
            tmp_path = Path(tmp_dir)
            tmp_published_config = tmp_path / "config.json"
            with open(tmp_published_config, "w", encoding="utf-8") as f:
                tamm_json.dump(published_model_config, f)
            return self.publish_directory(tmp_path)

    def _maybe_update_model_id(
        self,
        config: "PublishedModelConfig",
        model_id: Optional[str] = None,
        project_id: Optional[str] = None,
        version_id: Optional[str] = None,
    ) -> "PublishedModelConfig":
        resolved_model_id = config.model_id if model_id is None else model_id
        try:
            config.model_id = self._get_model_id(
                resolved_model_id, project_id, version_id
            )
        except ValueError:
            pass
        return config

    # pylint: disable=unused-argument
    def _get_model_id(
        self,
        base_model_id: Optional[str] = None,
        project_id: Optional[str] = None,
        version_id: Optional[str] = None,
    ) -> str:
        """
        Get model ID by parts
        Args:
            base_model_id: Basename of the model
            project_id: Optional project ID for supported backends
            version_id: Optional version ID for supported backends

        Returns: A valid model ID for the backend

        """
        if not base_model_id:
            raise ValueError(
                f"base_model_id must be a valid string, got {base_model_id}"
            )
        return base_model_id

    def publish_model_config(
        self,
        model_config: "ModuleConfig",
        model_id: Optional[str] = None,
        project_id: Optional[str] = None,
        version_id: Optional[str] = None,
    ) -> Any:
        if model_id is None:
            raise ValueError(
                "`model_id` must be specified to publish subclasses of `ModuleConfig`"
            )

        published_model_config = PublishedModelConfig(
            model_id=self._get_model_id(model_id, project_id, version_id),
            model_config=model_config,
        )
        return self.publish_published_model_config(published_model_config)

    def publish_file(
        self,
        file: Path,
        model_id: Optional[str] = None,
        project_id: Optional[str] = None,
        version_id: Optional[str] = None,
    ) -> Any:
        with open(file, "r", encoding="utf-8") as f:
            model_config = tamm_json.load(f)
        if isinstance(model_config, PublishedModelConfig):
            return self.publish_published_model_config(
                model_config,
                model_id=model_id,
                project_id=project_id,
                version_id=version_id,
            )
        if isinstance(model_config, ModuleConfig):
            return self.publish_model_config(
                model_config,
                model_id=model_id,
                project_id=project_id,
                version_id=version_id,
            )
        raise ValueError(
            f"'{file}' must be either `PublishedModelConfig` or `ModuleConfig`, "
            f"got {type(model_config)}"
        )

    def publish_directory(
        self,
        directory: Path,
        model_id: Optional[str] = None,
        project_id: Optional[str] = None,
        version_id: Optional[str] = None,
    ) -> Any:
        """
        Publishes the contents of ``directory`` as ``model_id``

        .. admonition:: Input requirements

            ``directory`` must have single ``config.json`` which is the valid
            :class:`PublishedModelConfig` for the candidate model.

        If implementation supports, checkpoints under ``directory`` will
        also be published.

        Args:
            directory: Directory to be published
            model_id: Model ID override name of the model
                          (required if ``payload`` is not :class:`PublishedModelConfig`)
            project_id: Optional project ID for supported backends
            version_id: Optional version ID for supported backends

        Returns:

        """
        if not directory.is_dir():
            raise ValueError(f"{directory} must be a directory")
        config_file = directory / "config.json"
        if not config_file.is_file():
            raise ValueError(
                f"PublishedModelConfig '{config_file}' must exist in this exact path"
            )
        with open(config_file, "r", encoding="utf-8") as f:
            model_config = tamm_json.load(f)
        if not isinstance(model_config, PublishedModelConfig):
            raise ValueError(
                f"'{model_config}' must be `PublishedModelConfig`, "
                f"got {type(model_config)}"
            )
        model_config = self._maybe_update_model_id(
            model_config, model_id, project_id, version_id
        )
        with open(config_file, "w", encoding="utf-8") as f:
            tamm_json.dump(model_config, f)
        return self._publish_directory(directory)

    @abc.abstractmethod
    def _publish_directory(
        self,
        directory: Path,
    ) -> Any:
        """
        Abstract method to be implemented in subclasses. Subclasses can safely
        assume there's a :class:`PublishedModelConfig` at ``<directory>/config.json``

        Args:
            directory: Directory which contains model artifacts (model config and ckpt)

        Returns: A handle of the published model

        """
