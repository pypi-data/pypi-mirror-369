import os
import glob
import requests
from typing import List
from .config import Config

def upload_file(filepath: str, api_key: str, team_id: str, project_id: str, testrun_id: str, api_base_url: str) -> List[dict]:
	if not os.path.isfile(filepath):
		raise FileNotFoundError(f"File not found: {filepath}")
	if not filepath.lower().endswith(tuple(Config().allowed_extensions)):
		raise ValueError(f"Only '{tuple(Config().allowed_extensions)}' files are allowed")

	http_method = 'FILE'  # 'POST' or 'GET'
	api_endpoint = 'tbreports/uploadAutomationRunResults'

	if not api_key:
		api_key = Config().default_api_key

	params_dict = { 'teamId': team_id, 'appId': project_id, 'reportId': testrun_id, 'isCLI': 1 }

	files = {'attachments': open(filepath, 'rb')}

	# Call the curl_request method to upload response
	response =  curl_request(api_base_url, http_method, api_endpoint, api_key, params_dict, files)

	# Error Check
	if response['status'] != 'OK' or response['apiResponse']['status'] != 'OK':
		return response

	return response

def upload_xml_files_from_folder(folder: str, api_key: str, team_id: str, project_id: str, testrun_id: str, api_base_url: str) -> List[dict]:
	filepaths = glob.glob(os.path.join(folder, tuple(Config().allowed_extensions)))
	if not filepaths:
		raise FileNotFoundError(f"No '{tuple(Config().allowed_extensions)}' files found in folder '{folder}'")

	http_method = 'FILE'
	api_endpoint = 'tbreports/uploadAutomationRunResults'

	if not api_key:
		api_key = Config().default_api_key

	params_dict = { 'teamId': team_id, 'appId': project_id, 'reportId': testrun_id }

	# Build the 'attachments' file list for all xml files
	files = [('attachments', open(fp, 'rb')) for fp in filepaths]

	# Call the curl_request method to upload respons
	response = curl_request(api_base_url, http_method, api_endpoint, api_key, params_dict, files)

	if response['status'] != 'OK' or response['apiResponse']['status'] != 'OK':
		return response

	return response

def curl_request(api_base_url="http://localhost/api.appachhi.com/", http_method='POST', api_endpoint='', api_key='', params_dict=None, files=None):
	response = _initialize_response()

	http_method, response = _validate_params(http_method, api_endpoint, api_key, params_dict, response)
	headers = _build_headers(api_key, http_method)

	try:
		api_url = _build_api_url(api_base_url, api_endpoint, http_method, params_dict)
		response = _make_request(http_method, api_url, headers, params_dict, response, files)
	except requests.RequestException as e:
		raise ValueError(f"ERROR: {str(e)}")
		response['message'] = str(e)
		return response

	return response

def _initialize_response():
	return {
		'status': 'ERROR',
		'message': ''
	}

def _validate_params(http_method, api_endpoint, api_key, params_dict, response):
	http_method = http_method.upper()
	if http_method not in ['GET', 'POST', 'FILE']:
		raise ValueError(f"httpMethod=[{http_method}] is not valid/supported")
		response['message'] = f"httpMethod=[{http_method}] is not valid/supported"
		return http_method, response

	if not api_endpoint:
		raise ValueError(f"apiEndpoint=[{api_endpoint}] is missing")
		response['message'] = f"apiEndpoint=[{api_endpoint}] is missing"
		return http_method, response

	if not api_key:
		raise ValueError(f"INFO: apiKey=[{api_key}] is missing. Default api Key has been set")
		response['message'] = "api key is missing"
		return http_method, response

	if params_dict is None or not isinstance(params_dict, dict):
		raise ValueError(f"Parameters not set correctly to make request")
		params_dict = {}

	return http_method, response

def _build_headers(api_key, http_method):

	expect_header = {"Expect": "100-continue"} if http_method == 'POST' else {}
	headers = {
		'Accept': 'application/json',
		'Authorization': f'Basic {api_key}'
	}

	# Merge the Expect header if it exists
	headers.update(expect_header)

	return headers

def _build_api_url(api_base_url, api_endpoint, http_method, params_dict):
	if http_method == 'GET' and params_dict:
		query_string = '&'.join(f"{key}={value}" for key, value in params_dict.items())
		api_endpoint += f"?{query_string}"
	return api_base_url + api_endpoint

def _make_request(http_method, api_url, headers, params_dict, response, file):
	if http_method == 'POST':
		resp = requests.post(api_url, headers=headers, data=params_dict)
	elif http_method == 'FILE':
		resp = requests.post(api_url, headers=headers, files=file, data=params_dict)
	else:
		resp = requests.get(api_url, headers=headers)

	if resp.status_code != 200:
		raise ValueError(f"Request ERROR: {resp.text}")
		response['message'] = resp.text
		return response

	try:
		api_response = resp.json()
	except ValueError:
		raise ValueError(f"Response could not be parsed")
		response['message'] = 'Could not parse JSON response'
		return response

	if not isinstance(api_response, dict):
		raise ValueError(f"Could not fetch details from the API.")
		response['message'] = 'Could not fetch details from the API'
		response['apiResponse'] = api_response
		return response

	response['status'] = 'OK'
	response['message'] = 'Successfully fetched the API array.'
	response['apiResponse'] = api_response

	if api_response.get('status') != 'OK':
		raise ValueError(f"ERROR: {api_response.get('message')}")
		return response

	return response