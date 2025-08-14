# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
# algorithm specialized in incorporating tokens with the gpt and sapi standard
class SapiensEmbedding:
	def __init__(self):
		from json import loads
		from ast import literal_eval
		from urllib.request import urlopen
		from os.path import isfile
		from sapiens_tokenizer import SapiensTokenizer
		self.__loads = loads
		self.__literal_eval = literal_eval
		self.__urlopen = urlopen
		self.__isfile = isfile
		self.__sapiens_tokenizer = SapiensTokenizer()
	def __load_json(self, string_content=''):
		json_content = {}
		string_content = str(string_content)
		try: json_content = self.__loads(string_content)
		except: json_content = self.__literal_eval(string_content)
		return json_content
	def __read_json(self, file_path=''):
		json_content = {}
		file_text, file_path = '', str(file_path).strip()
		if file_path.startswith(('http://', 'https://', 'www.')):
			try:
				connection = self.__urlopen(file_path)
				file_text = rf"{connection.read().decode('utf-8')}".strip()
			except: file_text = ''
		if not file_text and file_path and self.__isfile(file_path):
			with open(file_path, 'r', encoding='utf-8') as text_file: file_text = rf'{text_file.read()}'.strip()
		json_content = self.__load_json(string_content=file_text)
		return json_content
	def load_vocabulary(self, file_path=''):
		try:
			if not file_path: return self.__sapiens_tokenizer.load_vocabulary(file_path=file_path)
			json_content = self.__read_json(file_path=file_path)
			self.__sapiens_tokenizer.vocabulary_size = int(json_content.get('vocabulary_size', 0))
			self.__sapiens_tokenizer.token_to_index = dict(json_content.get('token_to_index', {}))
			self.__sapiens_tokenizer.index_to_token = dict(json_content.get('index_to_token', {}))
			self.__sapiens_tokenizer.pattern = str(json_content.get('pattern', 'sapi-5')).lower().strip()
			if not self.__sapiens_tokenizer.token_to_index and self.__sapiens_tokenizer.index_to_token: self.__sapiens_tokenizer.token_to_index = self.__sapiens_tokenizer.key_to_value(dictionary=self.__sapiens_tokenizer.index_to_token)
			if not self.__sapiens_tokenizer.index_to_token and self.__sapiens_tokenizer.token_to_index: self.__sapiens_tokenizer.index_to_token = self.__sapiens_tokenizer.key_to_value(dictionary=self.__sapiens_tokenizer.token_to_index)
			if self.__sapiens_tokenizer.pattern != 'sapi-0':
				if self.__sapiens_tokenizer.pattern == 'sapi-1': tokens_length = 2
				elif self.__sapiens_tokenizer.pattern == 'sapi-2': tokens_length = 3
				elif self.__sapiens_tokenizer.pattern == 'sapi-3': tokens_length = 4
				elif self.__sapiens_tokenizer.pattern == 'sapi-4': tokens_length = 5
				else: tokens_length = 0
				if tokens_length >= 2: text_to_list = self.__sapiens_tokenizer._SapiensTokenizer__text_to_list
				else: text_to_list = self.__sapiens_tokenizer._SapiensTokenizer__text_to_list_sapi5
				self.__sapiens_tokenizer.encode = lambda strings: [self.__sapiens_tokenizer.token_to_index[token] for token in text_to_list(text=strings, tokens_length=tokens_length, is_sorted=False)]
			else: self.__sapiens_tokenizer.encode = lambda strings: [self.__sapiens_tokenizer.token_to_index[token] for token in strings]
			self.__sapiens_tokenizer.decode = lambda indexes: ''.join([self.__sapiens_tokenizer.index_to_token[str(index)] for index in indexes])
			return True
		except Exception as error:
			print('ERROR in SapiensEmbedding.load_vocabulary: ' + str(error))
			return self.__sapiens_tokenizer.load_vocabulary(file_path=file_path)
	def text_to_embedding(self, text_data='', length=None, pattern='', method='truncate'):
		try:
			embedding = []
			if length is not None: length = max(0, int(length)) if type(length) in (bool, int, float) else 0
			if not text_data or length == 0: return embedding
			pattern, method = str(pattern).lower().strip(), str(method).lower().strip()
			text_data = rf'{text_data}'.strip()
			if method not in ('truncate', 'average'): method = 'truncate'
			if method == 'truncate' or length is None: embedding = self.__sapiens_tokenizer.to_encode(text_data=text_data, length=length, pattern=pattern)
			else:
				embedding = self.__sapiens_tokenizer.to_encode(text_data=text_data, length=None, pattern=pattern)
				embedding_length = len(embedding)
				if embedding_length < length:
					complement_id = self.__sapiens_tokenizer.to_encode(text_data='_', length=None, pattern=pattern)
					embedding += complement_id*(length-embedding_length)
				else:
					embedding_limit = max(0, length-1)
					initial_embedding = embedding[:embedding_limit]
					remaining_embedding = embedding[embedding_limit:]
					last_token_id = int(sum(remaining_embedding)/max(1, len(remaining_embedding)))
					embedding = initial_embedding+[last_token_id]
			return embedding
		except Exception as error:
			print('ERROR in SapiensEmbedding.text_to_embedding: ' + str(error))
			return []
	def embedding_to_text(self, embedding=[], length=None, pattern='', strip=True):
		try:
			text_data = ''
			embedding = list(embedding) if type(embedding) in (tuple, list) else []
			if length is not None: length = max(0, int(length)) if type(length) in (bool, int, float) else 0
			if not embedding or length == 0: return text_data
			pattern = str(pattern).lower().strip()
			strip = bool(strip) if type(strip) in (bool, int, float) else True
			text_data = self.__sapiens_tokenizer.to_decode(embedding=embedding, length=length, pattern=pattern)
			if '_' in text_data: text_data = text_data.rstrip('_')+' '*(len(text_data)-len(text_data.rstrip('_')))
			return text_data if not strip else text_data.strip()
		except Exception as error:
			print('ERROR in SapiensEmbedding.embedding_to_text: ' + str(error))
			return ''
	def count_tokens(self, text_data_or_embedding='', pattern=''):
		try: return self.__sapiens_tokenizer.count_tokens(text_data_or_embedding=text_data_or_embedding, pattern=pattern)
		except Exception as error:
			print('ERROR in SapiensEmbedding.count_tokens: ' + str(error))
			return 0
# --------------------------> A SAPIENS TECHNOLOGY®️ PRODUCTION) <--------------------------
