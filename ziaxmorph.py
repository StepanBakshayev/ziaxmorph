import json
import re
from enum import Enum
from itertools import tee
from typing import List, Any

from pydantic import BaseModel, constr, ValidationError, conint
from devtools import debug
from pydantic.error_wrappers import flatten_errors


class RequestData(BaseModel):
	sentence: constr(min_length=2)#, regex=re.compile(r''))


Status = Enum('Status', zip(*tee('ok error'.split(' '))), module=__name__, type=str)


class ResponseData(BaseModel):
	status: Status = Status.ok
	declined_word: List[str]
	num_words: conint(gt=0)


class ResponseError(BaseModel):
	status: Status = Status.error
	description: Any


def response(start_response, status: str, data: BaseModel):
	body = data.json(ensure_ascii=False).encode('utf-8')
	headers = (
		('Content-Type', 'application/json'),
		('Content-Length', str(len(body)))
	)
	start_response(status, headers)
	return body,


def handler(request: RequestData) -> BaseModel:
	words = request.sentence.split(' ')
	result = ResponseData(
		status=Status.ok, declined_word=[words[0]], num_words=len(words)
	)
	return result


def application(environ, start_response):
	if environ['PATH_INFO'] != '/':
		return response(start_response, '404 Not Found', ResponseError(description='not found'))

	if environ['CONTENT_TYPE'] != 'application/json':
		return response(start_response, '400 Bad Request', ResponseError(description='wrong content type'))

	if environ['HTTP_KEY'] != 'ziax':
		return response(start_response, '401 Unauthorized', ResponseError(description='not allowed'))

	# XXX: what is the way to handle variable content length of body (I forget name of such encoding of http message).
	try:
		request_body_size = int(environ.get('CONTENT_LENGTH', 0))
	except ValueError:
		request_body_size = 0

	request_body = environ['wsgi.input'].read(request_body_size)
	try:
		request_data = RequestData.parse_raw(request_body)
	except ValidationError as e:
		return response(
			start_response,
			'422 Unprocessable Entity',
			ResponseError(
				description=list(flatten_errors(e.raw_errors, e.model.__config__, loc=('body',)))
			)
		)

	try:
		result = handler(request_data)
		status = '200 OK'
	except Exception as e:
		result = ResponseError(description=str(e))
		status = '500 Internal Server Error'

	return response(start_response, status, result)
