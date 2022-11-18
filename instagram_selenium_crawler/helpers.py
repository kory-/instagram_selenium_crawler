import json
import re
import time


def response_log(driver, pattern):
    time.sleep(0.1)
    logs_raw = driver.get_log("performance")
    logs = [json.loads(lr["message"])["message"] for lr in logs_raw]

    target_logs = [x for x in logs if x['method'] == "Network.responseReceived" and len(re.findall(pattern, x["params"]["response"]["url"])) > 0]

    if len(target_logs) > 0:
        return target_logs[0]

    return response_log(driver, pattern)


def response_log_body(driver, request_id):
    response = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': request_id})
    return response['body']


def response_and_request_log(driver, pattern):
    time.sleep(0.1)
    logs_raw = driver.get_log("performance")
    logs = [json.loads(lr["message"])["message"] for lr in logs_raw]

    response_target_logs = [x for x in logs if x['method'] == "Network.responseReceived" and len(re.findall(pattern, x["params"]["response"]["url"])) > 0]
    request_target_logs = [x for x in logs if x['method'] == "Network.requestWillBeSent" and len(re.findall(pattern, x["params"]["request"]["url"])) > 0]

    if len(response_target_logs) > 0 and len(request_target_logs) > 0:
        return response_target_logs[0], request_target_logs[0]

    return response_and_request_log(driver, pattern)
