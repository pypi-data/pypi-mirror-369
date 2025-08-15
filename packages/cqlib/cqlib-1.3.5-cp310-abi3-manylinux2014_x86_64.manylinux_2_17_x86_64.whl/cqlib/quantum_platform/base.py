# This code is part of cqlib.
#
# Copyright (C) 2024 China Telecom Quantum Group, QuantumCTek Co., Ltd.,
# Center for Excellence in Quantum Information and Quantum Physics.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""
Base class for all quantum platform
"""
import json
import logging
import time
from enum import Enum
from typing import Optional, Union, List
from functools import wraps
import requests

from cqlib.exceptions import CqlibRequestError, CqlibInputParaError
from cqlib.utils.laboratory_utils import LaboratoryUtils

logger = logging.getLogger('cqlib')


class QuantumLanguage(Enum):
    """
    Quantum circuit language
    """
    QCIS = 'qcis'
    ISQ = 'isq'
    QUINGO = 'quingo'


def format_circuit(circuit: str):
    """
    Parse circuit description and generate
    experiment script and extract number of measured qubits.

    Args:
        circuit: circuit content

    Returns:
     circuit
    """
    content = []
    for line in circuit.split('\n'):
        line = line.strip()
        if line:
            content.append(line)

    return '\n'.join(content)


class BasePlatform:
    """
    base class for all platforms
    """

    # scheme
    SCHEME = 'https'
    # domain
    DOMAIN = ''
    # login path
    LOGIN_PATH = ''
    # create lab path
    CREATE_LAB_PATH = ''
    # save exp path
    SAVE_EXP_PATH = ''
    # create exp and run path
    CREATE_EXP_AND_RUN_PATH = ''
    # query exp path
    QUERY_EXP_PATH = ''
    # download config path
    DOWNLOAD_CONFIG_PATH = ''
    # qcis check regular path
    QCIS_CHECK_REGULAR_PATH = ''
    # get exp circuit path
    GET_EXP_CIRCUIT_PATH = ''
    # machine list path
    MACHINE_LIST_PATH = ''
    # machine config path
    MACHINE_CONFIG_PATH = ''
    # re execute path
    RE_EXECUTE_TASK_PATH = ''
    # stop running exp path
    STOP_RUNNING_EXP_PATH = ''

    def __init__(self, login_key: str, auto_login: bool = True, machine_name: str = None):
        """
        Platform initialization

        Args:
            login_key: API Token under personal center on the web.
            auto_login: run login if true
            machine_name: quantum machine or simulator name
        """
        self.login_key = login_key
        self.auto_login = auto_login
        self.machine_name = machine_name
        self.access_token = ''

        if self.auto_login:
            self.login()

    def login(self) -> int:
        """
        Authenticate username and password and return user credit

        Returns:
             log in state, 1 means pass authentication, 0 means failed
        """
        data = {
            'grant_type': 'openId',
            'openId': self.login_key,
            'account_type': 'member'
        }
        headers = {"Authorization": "Basic d2ViQXBwOndlYkFwcA=="}
        # pylint: disable=missing-timeout
        res = requests.post(url=f'{self.SCHEME}://{self.DOMAIN}{self.LOGIN_PATH}',
                            headers=headers, data=data)
        if res.status_code != 200:
            raise CqlibRequestError('Login failed: request interface failed', res.status_code)

        data = res.json()
        if data.get('code', -1) != 0:
            raise CqlibRequestError('Login failed')
        self.access_token = data.get('data').get('access_token')
        return self.access_token

    def set_machine(self, machine_name: str):
        """
        set the machine name.

        Args:
            machine_name: name of quantum computer or simulator.
        """
        self.machine_name = machine_name

    def create_lab(self, name: str, remark: str = '') -> str:
        """
        create a new lab, a collection of experiments.

        Args:
            name: new experiment collection Name.
            remark: experimental remarks.

        Returns:
            0 failed, not 0 successful, success returns the experimental set id
        """
        data = {
            "name": name,
            "remark": remark
        }
        result = self._send_request(path=self.CREATE_LAB_PATH, data=data, method='POST')
        return result.get('data').get('lab_id')

    def save_experiment(
            self,
            lab_id: str,
            circuit: str,
            name: Optional[str] = "",
            language: QuantumLanguage = QuantumLanguage.QCIS,
            **kwargs
    ):
        """
        save the experiment and return the experiment ID. (Will not run immediately)

        Args:
            lab_id: experiment lab ID
            circuit: experiment circuit
            name: experiment name
            language: Quantum computer language, including ['isq', 'quingo', 'qcis'].
            kwargs: Optional attachment key word args.

        kwargs Description
            noise: This parameter is a list of dictionaries, each describing a type of
            quantum noise model for simulations that utilize a noisy quantum simulator.
            Currently, only one noise model can be specified at a time, but future updates
            will allow multiple parameters.

            This parameter allows the configuration of different types of quantum noise which
            affects the simulation by altering the state of qubits. The accepted noise types
            and their corresponding parameters are as follows:
                **bit-flip**: Simulates the bit flip error, where a qubit state ∣0⟩ flips to ∣1⟩
                and vice versa. The parameter is the probability pp of a bit flip occurring,
                typically set to a default value of 0.1.
                ```
                noise=[{"noise_type": "bit-flip", "params": [0.1]}]
                ```

                **phase-flip**: Simulates the phase flip error, which flips the phase of a qubit.
                It takes a probability pp, with a typical default of 0.1.
                ```
                noise=[{"noise_type": "phase-flip", "params": [0.1]}]
                ```

                **depolarizing**: Simulates a depolarizing channel, which can randomly alter the
                state of a qubit to any other state. It is defined by a probability pp, commonly
                set to 0.1 by default.
                ```
                noise=[{"noise_type": "depolarizing", "params": [0.1]}]
                ```

                **decoherence**: Represents decoherence noise which is characterized by operational
                time, coherence time, and decoherence time. It's defined by the parameters:
                operation time (default 0.5), coherence time (default 200), and decoherence time
                (default 30).
                ```
                noise=[{"noise_type": "decoherence", "params": [0.5, 200, 30]}]
                ```

            quantum_state: This parameter specifies the state of the quantum simulation where only
            a single amplitude is simulated. It generally requires a parameter specifying the output
            state, with a default value of 0.
            ```
            quantum_state=1
            ```

        Returns:
            experiment id
        """
        if language.value == 'qcis':
            circuit = circuit.upper()
        exp_data = format_circuit(circuit)
        data = {
            "inputCode": exp_data,
            "lab_id": lab_id,
            "languageCode": language.value,
            "name": name,
            "source": "SDK",
            "computerCode": self.machine_name
        }
        if 'noise' in kwargs:
            data['noise'] = kwargs['noise']
        elif 'quantum_state' in kwargs:
            data['quantumState'] = kwargs['quantum_state']
        result = self._send_request(path=self.SAVE_EXP_PATH, data=data, method='post')
        return result.get('data').get('exp_id')

    def run_experiment(
            self,
            exp_id: str,
            num_shots: int = 12000,
            is_verify: bool = True
    ):
        """
        running the experiment returns the query result id.

        Args:
            exp_id: experimental id. the id returned by the save_experiment interface.
            num_shots: number of repetitions per experiment. Defaults to 12000.
            is_verify: Is the circuit verified.

        Returns:
            experiment task query id.
        """
        data = {
            "exp_id": exp_id,
            "shots": num_shots,
            "is_verify": is_verify,
            # "computerCode": self.machine_name,
            "source": "SDK",
        }
        return self.handler_run_experiment_result(data)

    # pylint: disable=too-many-arguments
    def submit_job(
            self,
            circuit: Optional[Union[List, str]] = None,
            exp_name: Optional[str] = "",
            parameters: Optional[List[List]] = None,
            values: Optional[List[List]] = None,
            num_shots: Optional[int] = 12000,
            lab_id: Optional[str] = None,
            exp_id: Optional[str] = None,
            language: QuantumLanguage = QuantumLanguage.QCIS,
            version: Optional[str] = "1",
            is_verify: Optional[bool] = True,
            **kwargs
    ):
        """
        submit experimental tasks.

        There are some parameter range limitations when using batch submission circuits.

        1. circuits length less than 50, num_shots maximum 100000, the number of measurement
            qubits is less than 15.

        2. circuits length greater than 50 but less than 100, num_shots maximum 50000,
           the number of measurement qubits is less than 30.

        3. circuits length greater than 100 but less than 600, num_shots maximum 10000,
           the number of measurement bits is less than the number of all available qubits.

        4. When the circuit is none, the exp_id cannot be none and the lab_id needs to be none,

        5. When the circuit is not none, when the circuit is multiple lines,
            the version and exp_id need to be none,
            and the line will be saved under the default collection if the lab_id or exp_name
            is not transmitted.

        6. When the circuit is not none, when the circuit is a single line, exp_id need to be none,
            version does not transmit to generate the default,
            lab_id or exp_name does not transmit the line is saved under the default collection.

        Args:
            circuit: experimental content, qcis. Defaults to None.
            exp_name: new experiment collection Name. Defaults to "exp0".
            parameters: parameters that need to be assigned in the experimental content.
            values: The values corresponding to the parameters that need to be assigned
                    in the experimental content. Defaults to None.
            num_shots: number of repetitions per experiment. Defaults to 12000.
            lab_id: the result returned by the create_experiment interface, experimental set id.
            exp_id: the result returned by the save_experiment interface, experimental id.
            language: quantum language code. Defaults to qcis.
            version: version description. Defaults to 'version01'.
            is_verify: Is the circuit verified.True verify, False do not verify.
            kwargs: Same as in `save_experiment`. Refer to the `save_experiment` function for
                    details on the accepted parameters and usage examples.

        Returns:
            Union[int, str]: If 0 failed, else return the query id if successful.
        """
        if isinstance(circuit, str):
            circuit = [circuit]
        if circuit is not None:
            if len(circuit) > 1:
                version = None
        else:
            if exp_id is None:
                raise CqlibInputParaError(
                    "When circuit is not defined, experiment id should be defined"
                    " but None has been given.")
            data = {
                "exp_id": exp_id,
                "shots": num_shots,
                "is_verify": is_verify,
                "source": "SDK",
            }
            return self.handler_run_experiment_result(data)
        if (
                circuit
                and parameters
                and values
                and len(parameters) == len(circuit) == len(values)
        ):
            laboratory_utils = LaboratoryUtils()
            new_circuit = laboratory_utils.assign_parameters(
                circuit, parameters, values
            )
            if not new_circuit:
                logger.error("Unable to assign a value to the circuits")
                return 0
        else:
            new_circuit = circuit

        data = {
            "exp_id": exp_id,
            "lab_id": lab_id,
            "inputCode": new_circuit,
            "languageCode": language.value,
            "name": exp_name,
            "shots": num_shots,
            "source": "SDK",
            "computerCode": self.machine_name,
            "experimentDetailName": version,
            "is_verify": is_verify,
        }
        if 'noise' in kwargs:
            data['noise'] = kwargs['noise']
        elif 'quantum_state' in kwargs:
            data['quantumState'] = kwargs['quantum_state']
        return self.handler_run_experiment_result(data)

    def handler_run_experiment_result(self, data):
        """
        Handles the request to save the result of running an experiment.

        Attempts to temporarily save the experiment results to the server.
        Returns a list of saved query IDs upon success; may reconnect and retry on failure.

        Args:
            data (dict): A dictionary containing the experiment results.

        Returns:
            list: A list of saved query IDs if successful; otherwise, returns 0.
        """
        # url = "/sdk/experiment/temporary/save"
        result = self._send_request(path=self.CREATE_EXP_AND_RUN_PATH, data=data, method="POST")
        if result == 0:
            return 0
        return result.get("data").get("query_ids")

    def query_experiment(
            self,
            query_id: Union[str, List[str]],
            max_wait_time: int = 120,
            sleep_time: int = 5
    ):
        """query experimental results

        Args:
            query_id: experiment task ids. The maximum count is 50.
            max_wait_time: maximum waiting time for querying experiments. Defaults to 60.
            sleep_time: If query result failed, take a break and start again.

        Returns:
            the experimental result list
        """
        if isinstance(query_id, str):
            query_id = [query_id]
        last_time = time.time() + max_wait_time
        while time.time() < last_time:
            try:
                data = {"query_ids": query_id}
                result = self._send_request(path=self.QUERY_EXP_PATH, data=data, method='POST')
                query_exp = result.get('data').get('experimentResultModelList')
                if query_exp and len(query_exp) == len(query_id):
                    return query_exp
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.error(e)
            logger.info('waiting for %d seconds', sleep_time)
            time.sleep(sleep_time)
        raise CqlibRequestError("Failed to query the experimental result.")

    def download_config(
            self,
            read_time: str = None,
            machine: str = None
    ):
        """download experimental parameters.

        Args:
            read_time: select configuration data according to the reading time,
                and the parameter format is yyyy-MM-dd HH:mm:ss, Defaults to None.
            machine: machine name

        Returns:
            0 failed, not 0 successful, success returns the experimental parameters.
        """
        if not machine:
            machine = self.machine_name
        result = self._send_request(path=f'{self.DOWNLOAD_CONFIG_PATH}/{machine}',
                                    method='GET', params={'readTime': read_time})
        cfg = result.get('data')
        if isinstance(cfg, str):
            cfg = json.loads(cfg)
        return cfg

    def qcis_check_regular(
            self,
            qcis_raw: str
    ):
        """qcis regular check,normal returns 1, abnormal returns 0

        Args:
            qcis_raw: qcis circuit

        Returns:
            0 failed, 1 success
        """
        data = {
            "computerCode": self.machine_name,
            "qcis": qcis_raw
        }
        resp = self._send_request(path=self.QCIS_CHECK_REGULAR_PATH, method='POST',
                                  data=data, raise_for_code=False)
        return resp['code'] == 0

    def get_experiment_circuit(
            self,
            query_id: Union[str, List[str]]
    ):
        """
        According to the exp_id obtained experimental circuit

        Args:
            query_id: experimental id list. max length is 50

        Returns:
            the experimental circuit,
            The parameters of the returned experimental circuit include qcis、mapQcis and
            computerQcis. qcis is the line submitted by the user, mapQcis is the compiled
            circuit, computerQcis is a circuit submitted to a quantum computer.
        """
        if isinstance(query_id, str):
            query_id = [query_id]
        data = {"query_ids": query_id}
        result = self._send_request(path=self.GET_EXP_CIRCUIT_PATH, method='POST', data=data)
        return result.get('data')

    def query_quantum_computer_list(self):
        """Get a full list of quantum computers, a list of simulators,
        and show the corresponding states.

        Returns:
             List of quantum computers and related information.
        """
        result = self._send_request(self.MACHINE_LIST_PATH)
        computer_list_data = result.get('data')
        status_mapping = {
            0: 'running',
            1: 'calibration',
            2: 'under maintenance',
            3: 'off-line'
        }
        toll_mapping = {
            1: 'free',
            2: 'paid'
        }

        for item in computer_list_data:
            if 'code' in item:
                item['machineName'] = item.pop('code')
            if item['status'] in status_mapping:
                item['status'] = status_mapping[item['status']]
            else:
                item['status'] = 'unknown'
            if item['isToll'] in toll_mapping:
                item['isToll'] = toll_mapping[item['isToll']]
            else:
                item['isToll'] = '未知状态'
            for key in list(item.keys()):
                if item[key] is None:
                    del item[key]
        headers = computer_list_data[0].keys()
        table_data = []
        for row in computer_list_data:
            row_values = [row.get(key, None) for key in headers]  # 获取键对应的值，若键不存在则返回None
            table_data.append(row_values)
        return table_data

    def re_execute_task(
            self,
            query_id: Optional[str] = None,
            lab_id: Optional[str] = None,
    ):
        """
        Re-execute the experiment that has been run previously.

        Args:
            query_id: query id
            lab_id: resubmit all exp tasks in this lab set.

        Returns:
             the query id for resubmitting the experiment
        """
        if not lab_id and not query_id:
            raise CqlibInputParaError("Please provide lab_id or query_id.")
        data = {
            "lab_id": lab_id,
            "query_id": query_id
        }
        result = self._send_request(self.RE_EXECUTE_TASK_PATH, method='POST', data=data)
        return result.get('data')

    def stop_running_experiments(
            self,
            lab_id: Optional[str] = None,
            query_id: Optional[str] = None
    ):
        """
        Terminate recently running experiments

        Args:
            query_id: query id
            lab_id: Terminate all exp tasks in this lab set.

        Returns:
            the query id for stopped the experiment
        """
        if not lab_id and not query_id:
            raise CqlibInputParaError("Please provide lab_id or query_id.")
        data = {
            "lab_id": lab_id,
            "query_id": query_id
        }
        result = self._send_request(self.STOP_RUNNING_EXP_PATH, method='POST', data=data)
        return result.get('data')

    def get_machine_config(self, params: Optional):
        """
        Download qpu topology structure without authentication.

        Args:
            params: parameter input required by gplot module.

        Returns:
            data about qpu topology info.

        """
        result = self._send_request(path=f'{self.MACHINE_CONFIG_PATH}',
                                    method='GET', params=params)
        return result.get("data")

    @staticmethod
    def _reconnect_on_failure(func, max_retries=2, retry_delay=1):
        """
        Wraps a function to reconnect on failure.

        Args:
            func (Callable): The function to be decorated.
            max_retries (int, optional): Maximum number of retries. Defaults to 2.
            retry_delay (int, optional): Time to wait between retries. Defaults to 1 second.

        Returns:
            Callable: A wrapped function that retries on failure.

        Raises:
            Exception: If the maximum number of retries is exceeded.
        """

        @wraps(func)
        def wrapper(self, *args, **kwargs):
            retries = 0
            last_error = None
            while retries < max_retries:
                retries += 1
                try:
                    result = func(self, *args, **kwargs)
                    return result
                except CqlibRequestError as cq_e:
                    last_error = cq_e
                    logger.warning(
                        "%s execution failed\ntry count:%s \nerror info: \n%s",
                        func.__name__, retries, cq_e
                    )
                    if cq_e.status_code == 401:
                        # status 401 code means access token has expired or being invalid.
                        logger.warning("user's token has expired, try to log in again.")
                        self.login()
                        time.sleep(retry_delay)
                except Exception as cq_e:  # pylint: disable=broad-exception-caught
                    last_error = cq_e

            if last_error:
                raise last_error

            raise CqlibRequestError(
                f"function:[{func.__name__}] Max retries exceeded. "
                f"Attempt {max_retries} times failed. "
            )

        return wrapper

    # pylint: disable=too-many-arguments
    @_reconnect_on_failure
    def _send_request(
            self,
            path: str,
            method: str = 'GET',
            data=None,
            params=None,
            raise_for_code=True
    ):
        """
        send request to server and return response data

        Args:
            path: request path
            method: request method
            data: request data
            params: request params
            raise_for_code: request params

        Returns:

        """
        url = f'{self.SCHEME}://{self.DOMAIN}{path}'
        if self.access_token:
            headers = {
                "basicToken": self.access_token,
                "Authorization": f'Bearer {self.access_token}'
            }
        else:
            headers = None
        # pylint: disable=missing-timeout
        res = requests.request(method.upper(), url, json=data, headers=headers, params=params)
        if res.status_code != 200:
            raise CqlibRequestError(f'Request API failed: {res.text}', res.status_code)
        result = res.json()
        if raise_for_code and result.get('code', -1) != 0:
            raise CqlibRequestError(f'Request error: {res.text}')
        return result
