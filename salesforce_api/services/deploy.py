import time
from base64 import b64encode
from .. import exceptions, const, config
from ..utils import misc
from ..models import deploy as models
from . import base


class Deploy(base.SoapService):
    def _get_zip_content(self, input_file) -> str:
        if isinstance(input_file, str):
            input_file = open(input_file, 'rb')
        return b64encode(
            input_file.read()
        ).decode('utf-8')

    def deploy(self, input_zip, options: models.Options = models.Options()) -> 'Deployment':
        result = self._post(action='deploy', message_path='deploy/deploy.msg', message_attributes={
            'zip_file': self._get_zip_content(input_zip),
            'options': options.as_xml()
        })
        if result.has('soapenv:Envelope/soapenv:Body/soapenv:Fault/faultcode'):
            raise exceptions.DeployCreateError(result.get_value('soapenv:Envelope/soapenv:Body/soapenv:Fault/faultstring'))
        return Deployment(self, result.get_value('soapenv:Envelope/soapenv:Body/deployResponse/result/id'))

    def check_deploy_status(self, async_process_id: str) -> models.Status:
        result = self._post(action='checkDeployStatus', message_path='deploy/status.msg', message_attributes={
            'async_process_id': async_process_id
        })

        result = result.get('soapenv:Envelope/soapenv:Body/checkDeployStatusResponse/result')

        status = models.Status(result.get_value('status'), result.get_value('stateDetail', None), models.DeployDetails(
            int(result.get_value('numberComponentsTotal')),
            int(result.get_value('numberComponentErrors')),
            int(result.get_value('numberComponentsDeployed'))
        ), models.DeployDetails(
            int(result.get_value('numberTestsTotal')),
            int(result.get_value('numberTestErrors')),
            int(result.get_value('numberTestsCompleted'))
        ))

        if status.status.lower().strip() == 'failed':
            for failure in result.get_list('details/componentFailures'):
                status.components.append_failure(models.ComponentFailure(
                    failure.get('componentType'),
                    failure.get('fileName'),
                    failure.get('problemType'),
                    failure.get('problem')
                ))

            for failure in result.get_list('details/runTestResult/failures'):
                status.tests.append_failure(models.UnitTestFailure(
                    failure.get('name'),
                    failure.get('methodName'),
                    failure.get('message'),
                    failure.get('stackTrace')
                ))

        return status

    def cancel(self, async_process_id: str) -> bool:
        result = self._post(action='cancelDeploy', message_path='deploy/cancel.msg', message_attributes={
            'async_process_id': async_process_id
        })
        return misc.parse_bool(result.get_value('soapenv:Envelope/soapenv:Body/cancelDeployResponse/result/done'))


class Deployment:
    def __init__(self, deploy_service: Deploy, async_process_id: str):
        self.deploy_service = deploy_service
        self.async_process_id = async_process_id
        self.start_time = time.time()

    def get_elapsed_seconds(self):
        return time.time() - self.start_time

    def get_elapsed_time(self):
        return time.strftime("%H:%M:%S", time.gmtime(self.get_elapsed_seconds()))

    def cancel(self) -> bool:
        return self.deploy_service.cancel(self.async_process_id)

    def get_status(self) -> models.Status:
        return self.deploy_service.check_deploy_status(self.async_process_id)

    def is_done(self):
        return self.get_status().status in const.STATUSES_DONE

    def has_failed(self):
        return self.get_status().status == const.STATUS_FAILED

    def has_succeeded(self):
        return self.get_status().status == const.STATUS_SUCCEEDED

    def wait(self, tick: callable = None):
        while True:
            status = self.get_status()
            if tick is not None and callable(tick):
                tick(status)
            if status.status in const.STATUSES_DONE:
                break
            time.sleep(config.DEPLOY_SLEEP_SECONDS)
