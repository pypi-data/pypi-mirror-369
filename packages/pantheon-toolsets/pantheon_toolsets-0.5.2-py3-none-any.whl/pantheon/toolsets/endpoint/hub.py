from pathlib import Path
import asyncio
import yaml

from executor.engine import Engine
from executor.engine.job.extend import SubprocessJob

from ..utils.toolset import ToolSet, tool
from ..utils.log import logger


class EndpointHub(ToolSet):
    def __init__(self, config_dir: str | Path, workspace_base_path: str | Path, worker_params: dict | None = None):
        self.config_dir = Path(config_dir)
        self.endpoint_config_paths: dict[str, str] = {}
        self.endpoint_configs: dict[str, str] = {}
        self.endpoints: dict[str, dict] = {}
        self.load_endpoint_config_paths()
        self.workspace_base_path = Path(workspace_base_path)
        self.workspace_base_path.mkdir(parents=True, exist_ok=True)
        self.engine = Engine()
        self.jobs: dict[str, SubprocessJob] = {}
        super().__init__("endpoint-hub", worker_params=worker_params)

    def load_endpoint_config_paths(self):
        for config_file in self.config_dir.glob("*.yaml"):
            with open(config_file, "r") as f:
                self.endpoint_config_paths[config_file.stem] = config_file

    @tool
    async def list_configs(self) -> list[str]:
        return list(self.endpoint_configs.keys())

    @tool
    async def get_config(self, config_name: str) -> dict:
        return self.endpoint_configs[config_name]

    @tool
    async def new_endpoint(self, config_name: str, id_hash: str) -> dict:
        logger.info(f"New endpoint {config_name} with id_hash {id_hash}")
        if id_hash in self.endpoints:
            return {
                "success": False,
                "error": f"Endpoint {id_hash} already exists",
            }
        with open(self.endpoint_config_paths[config_name], "r") as f:
            config = yaml.safe_load(f)
        config["id_hash"] = id_hash
        workspace_path = self.workspace_base_path / id_hash
        workspace_path.mkdir(parents=True, exist_ok=True)
        config["workspace_path"] = str(workspace_path)
        self.endpoint_configs[id_hash] = config
        (workspace_path / ".endpoint-logs").mkdir(parents=True, exist_ok=True)
        tmp_config_file = workspace_path / ".endpoint-logs" / "endpoint_config.yaml"
        with open(tmp_config_file, "w") as f:
            yaml.dump(config, f)
        cmd = (
            f"python -m magique.ai.endpoint start "
            f"--config-path {tmp_config_file} "
        )
        log_file = workspace_path / ".endpoint-logs" / "endpoint.log"
        job = SubprocessJob(cmd, retries=10, redirect_out_err=str(log_file))
        await self.engine.submit_async(job)
        await job.wait_until_status("running")
        await asyncio.sleep(1)
        self.jobs[id_hash] = job
        with open(workspace_path / ".endpoint-logs" / "service_id.txt", "r") as f:
            service_id = f.read().strip()
        self.endpoints[id_hash] = {
            "service_id": service_id,
            "log_file": str(log_file),
        }
        return {
            "success": True,
            "service_id": service_id,
        }

    @tool
    async def get_endpoint(self, id_hash: str) -> dict:
        endpoint = self.endpoints.get(id_hash)
        if endpoint:
            return {
                "success": True,
                "service_id": endpoint["service_id"],
            }
        return {
            "success": False,
            "error": f"Endpoint {id_hash} not found",
        }

    @tool
    async def delete_endpoint(self, id_hash: str) -> dict:
        logger.info(f"Deleting endpoint {id_hash}")
        job = self.jobs.get(id_hash)
        if job:
            await job.cancel()
            del self.jobs[id_hash]
            del self.endpoints[id_hash]
            return {
                "success": True,
            }
        else:
            return {
                "success": False,
                "error": f"Endpoint {id_hash} not found",
            }

    async def run(self, log_level: str = "INFO"):
        while True:
            try:
                await super().run(log_level)
            except Exception as e:
                logger.error(f"Error running endpoint hub: {e}")
                await asyncio.sleep(1)
                logger.info(f"Restarting endpoint hub")
