import pytest
from devtools import debug
from pydantic import ValidationError

from ziaxmorph import RequestData, handler


def test_constrain():
	# empty
	with pytest.raises(ValidationError):
		RequestData(sentence='')

	# numbers and special characters
	with pytest.raises(ValidationError):
		RequestData(sentence='123123#523570!@!#2;;')

	# mix of alphabets
	with pytest.raises(ValidationError):
		RequestData(sentence='Hello, МИр!')

	# phase
	RequestData(sentence='Здравствуй  ,   Мир  !  ')

	# title number
	RequestData(sentence='1 Мая.')


def test_handler():
	result = handler(RequestData(sentence='Мир  ! Труд, май.'))
	assert result.num_words == 3
	assert result.declined_word == [
		'мир',
		'мира',
		'миру',
		'мир',
		'миром',
		'мире',
		'миры',
		'миров',
		'мирам',
		'миры',
		'мирами',
		'мирах',
		'миру',
		'миру',
	]
