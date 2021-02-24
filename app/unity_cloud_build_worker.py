import logging
from aiohttp import ClientSession
from config.config import UnityCloudBuildConfig


class UnityCloudBuildWorker(object):
    def __init__(self, config: UnityCloudBuildConfig):
        self._log_tag = f'[UnityCloudBuildWorker:{config.project_name}]'
        self._logger = logging.getLogger(__name__)
        self._base_url = config.base_url
        self._project_id = config.project_id
        self._cloud_build_targets = config.cloud_build_targets
        self._supported_builds = list(self._cloud_build_targets.keys())
        self._session = None
        self._base_header = {
            'Content-Type': 'application/json',
            'Authorization': f'Basic {config.api_key}',
        }

    async def start_worker(self):
        assert self._session is None
        self._session = ClientSession()

    async def stop_worker(self):
        if self._session is not None:
            await self._session.close()
            self._session = None

    def cmd_supported_builds(self) -> list:
        return self._supported_builds

    async def cmd_start_build(self, build_target: str) -> str:
        build_target_id = self._cloud_build_targets.get(build_target, None)
        if build_target_id is None:
            return f'Unsupported build target: {build_target}'

        url = f'{self._base_url}/projects/{self._project_id}/buildtargets/{build_target_id}/builds'
        headers = {'clean': 'true'}
        response = await self._send(self._send_post, url, headers)
        result = await response.json() if response is not None else {}
        self._logger.info(f'{self._log_tag} cmd_start_build result: {result}')
        if result and len(result) > 0:
            result_msg = f"Start building {result[0]['buildTargetName']} | Branch: {result[0]['scmBranch']}"
        else:
            result_msg = f'Error starting build for target: {build_target}'
        return result_msg

    async def cmd_build_target_info(self, build_target: str) -> str:
        build_target_id = self._cloud_build_targets.get(build_target, None)
        if build_target_id is None:
            return f'Unsupported build target: {build_target}'

        url = f'{self._base_url}/projects/{self._project_id}/buildtargets/{build_target_id}'
        response = await self._send(self._send_get, url)
        result = await response.json() if response is not None else {}
        self._logger.info(f'{self._log_tag} cmd_build_target_info result: {result}')
        if result and len(result) > 0:
            result_msg = f"Name: {result['name']}\nPlatform: {result['platform']}\nBuild target: {build_target}\n" \
                         f"Status: {'enabled' if result['enabled'] else 'disabled'}\n" \
                         f"Unity version: {result['settings']['unityVersion']}\n" \
                         f"Branch: {result['settings']['scm']['branch']}\n"
        else:
            result_msg = f'Error getting build target info for: {build_target}'
        return result_msg

    async def _send(self, send_method: callable, url: str, headers: dict = None):
        try:
            if headers is not None:
                self._logger.info(f'{self._log_tag} Send get request with custom headers: {headers} | Url: {url}')
                headers.update(self._base_header)
            else:
                self._logger.info(f'{self._log_tag} Send get request without custom headers | Url: {url}')
                headers = self._base_header
            result = await send_method(url, headers)
            return result
        except Exception as e:
            self._logger.exception(f'{self._log_tag} Exception: {e}')
            return None

    async def _send_get(self, url: str, headers: dict = None):
        return await self._session.get(url=url, headers=headers, ssl=True)

    async def _send_post(self, url: str, headers: dict = None):
        return await self._session.post(url=url, headers=headers, ssl=True)
