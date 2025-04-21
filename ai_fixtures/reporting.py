import json
import logging
import os
import pathlib
import time
from datetime import datetime

import pytest
import requests

# Handles reporting and screenshots

LOGGER = logging.getLogger(__name__)


BROWSERSTACK_USERNAME = os.environ.get("BROWSERSTACK_USERNAME", "")
BROWSERSTACK_ACCESS_KEY = os.environ.get("BROWSERSTACK_ACCESS_KEY", "")
ROOT = os.curdir


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


def save_bs_info(driver):
    bs_info = driver.execute_script(
        'browserstack_executor: {"action": "getSessionDetails"}'
    )
    json_bs_info = json.loads(bs_info)
    filename = "bs_info.json"
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as file:
            data = json.load(file)
        if isinstance(data, list):
            data.append(json_bs_info)
            with open(filename, "w", encoding="utf-8") as file:
                json.dump(data, file, ensure_ascii=False, indent=4)
    else:
        with open(filename, "w", encoding="utf-8") as file:
            json.dump([json_bs_info], file, ensure_ascii=False, indent=4)


def test_failed_check(request, driver, playwright=False):
    result = "passed"
    reason = ""
    if request.node.rep_setup.failed:
        result = "error"
        reason = "Set up failed"
        print("setting up a test failed!", request.node.nodeid)
    elif request.node.rep_setup.passed:
        if request.node.rep_call.failed:
            result = "failed"
            reason = ""
            print("executing test failed", request.node.nodeid)
            take_screenshot(driver, request.node.nodeid, playwright)
    if request.fixturename == "mobile_driver":
        if pytest.run_type == "browserstack":
            upload_mobile_test_result_to_browserstack(driver, result, reason)
            if request.node.rep_call.failed:
                save_bs_info(driver)
    if not playwright:
        if pytest.driver is driver:
            if pytest.browserstack_session_id:
                if request.fixturename == "mobile_driver":
                    upload_mobile_test_result_to_browserstack(driver, result, reason)
                else:
                    update_test_result_to_browserstack(request.node.nodeid, result, reason)
    if playwright:
        update_test_result_to_browserstack(request.node.nodeid, result, reason)


def upload_test_result(request, driver, failed_count):
    new_failed_count = request.session.testsfailed
    result = "passed"
    if new_failed_count > failed_count:
        result = "failed"
    reason = ""
    if pytest.browserstack_session_id:
        upload_mobile_test_result_to_browserstack(driver, result, reason)
    if pytest.run_type == "lambdatest":
        driver.execute_script(f"lambda-status={result}")


def video_path():
    return os.path.join(ROOT, "videos/")


def screenshot_path(nodeid):
    test_root = pathlib.Path(__file__).resolve().parent.parent
    test_path = nodeid.replace("src/tests/e2e/tests/", "").split("::")
    print(f"Screen Shot Path {test_root}/screenshots")
    file_name = os.path.join(test_root, "screenshots", test_path[0], test_path[1])
    return file_name.replace(".py", "")


def take_screenshot(driver, nodeid, playwright=False):
    date = datetime.today().strftime("%Y%m%d_%H_%M_%S")
    file_path = screenshot_path(nodeid)
    test_case_name = nodeid.split("::")[2]
    os.makedirs(file_path, exist_ok=True)
    with_name = os.path.join(file_path, f"{test_case_name}_{date}.png")
    try:
        # driver.save_screenshot(with_name)
        if not playwright:
            driver.save_screenshot(with_name)
        else:
            driver.screenshot(with_name, full_page=True)
    except Exception as error:
        print(f"Failed to take screenshot - {error}")


def logs_path(nodeid):
    test_root = pathlib.Path(__file__).resolve().parent.parent
    test_path = nodeid.replace("src/tests/e2e/tests/", "").split("::")
    print(f"\nLog Path {test_root}/logs")
    file_name = os.path.join(test_root, "logs", test_path[0], test_path[1])
    return file_name.replace(".py", "")


def download_browserstack_logs(suite_name, project="automate"):
    session_id = pytest.browserstack_session_id

    url = (
        f"https://{BROWSERSTACK_USERNAME}:{BROWSERSTACK_ACCESS_KEY}"
        f"@api.browserstack.com/{project}/sessions/{session_id}.json"
    )
    response = requests.get(url, timeout=10)
    response_body = response.json()
    build_hashed_id = response_body["automation_session"]["build_hashed_id"]
    har_logs_url = None
    if project == "automate":
        har_logs_url = response_body["automation_session"]["har_logs_url"]
    elif project == "app-automate":
        har_logs_url = (
            f"https://{BROWSERSTACK_USERNAME}:{BROWSERSTACK_ACCESS_KEY}@api-cloud.browserstack.com"
            f"/app-automate/builds/{build_hashed_id}/sessions/{session_id}/networklogs"
        )
    har_log = download_browserstack_har_logs(suite_name, session_id, har_logs_url)
    return {"har_log": har_log}


def download_browserstack_har_logs(suite_name, session_id, har_logs_url, retries=10):
    if retries == 0:
        raise Exception("Can't download browserstack har logs.")
    response = requests.get(har_logs_url, timeout=10)
    if response.status_code == 200:
        response_body = response.json()
        file_path = logs_path(suite_name)
        os.makedirs(file_path, exist_ok=True)
        with_name = os.path.join(file_path, f"har-{session_id}.log")
        with open(with_name, "w", encoding="UTF-8") as file:
            json.dump(response_body, file, indent=0)
        return response_body
    # Since the browserstack network log is not stable,
    # longer the waiting time is better than rerun the whole test case
    time.sleep(10)
    return download_browserstack_har_logs(
        suite_name, session_id, har_logs_url, retries=retries - 1
    )


def update_test_result_to_browserstack(name, status, reason, project="automate"):
    session_id = pytest.browserstack_session_id
    response = requests.put(
        f"https://{BROWSERSTACK_USERNAME}:{BROWSERSTACK_ACCESS_KEY}"
        f"@api.browserstack.com/{project}/sessions/{session_id}.json",
        data={"name": name, "status": status, "reason": reason},
        timeout=10,
    )
    assert response.status_code == 200


def upload_mobile_test_result_to_browserstack(browser, result, reason):
    bs_status = (
        '() => browserstack_executor: {"action": "setSessionStatus", '
        '"arguments": {"status":"' + result + '", "reason": "' + reason + '"}}'
    )
    browser.evaluate(bs_status)

# def upload_mobile_test_result_to_browserstack(driver, result, reason):
#     bs_status = (
#         'browserstack_executor: {"action": "setSessionStatus", '
#         '"arguments": {"status":"' + result + '", "reason": "' + reason + '"}}'
#     )
#     driver.execute_script(bs_status)


def download_selenium_performance_log(suite_name, driver):
    date = datetime.today().strftime("%Y-%m-%d_%H_%M_%S")
    file_path = logs_path(suite_name)
    os.makedirs(file_path, exist_ok=True)
    with_name = os.path.join(file_path, f"selenium-{date}.log")
    with open(with_name, "w", encoding="UTF-8") as file:
        network_log = driver.get_log("performance")
        file.write(str(network_log))
        return network_log

def get_browserstack_selenium_session():
    if not hasattr(pytest, "browserstack_session_id"):
        return {}
    if not pytest.browserstack_session_id:
        return {}
    username = os.environ.get("BROWSERSTACK_USERNAME")
    access_key = os.environ.get("BROWSERSTACK_ACCESS_KEY")
    try:
        response = requests.get(
            f"https://api.browserstack.com/automate/sessions/{pytest.browserstack_session_id}.json",
            auth=(username, access_key),
            timeout=10,
        )
        return response.json()
    except requests.Timeout as timeout_exception:
        LOGGER.info("Request to BrowserStack API timed out: %s", timeout_exception)
        return {}

    except requests.RequestException as request_exception:
        LOGGER.info("Request to BrowserStack API failed: %s", request_exception)
        return {}


def get_browserstack_public_url():
    session = get_browserstack_selenium_session()
    data = session.get("automation_session", {})
    if not data:
        time.sleep(5)
        session = get_browserstack_selenium_session()
        data = session.get("automation_session", {})
    if data:
        return data.get("public_url")
    return "Not available"
