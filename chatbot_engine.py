import dialogflow_v2 as dialogflow
import uuid

#based on https://github.com/googleapis/dialogflow-python-client-v2/tree/master/samples

class DialogflowEngine():
	def __init__(self, credentials=None, project_id="athome-229904", session_id=None, language_code="en_us"):
		self.session_client = dialogflow.SessionsClient(credentials=credentials)
		self.intents_client = dialogflow.IntentsClient(credentials=credentials)
		self.entity_types_client = dialogflow.EntityTypesClient(credentials=credentials)
		self.session_entity_types_client = dialogflow.SessionEntityTypesClient(credentials=credentials)
		
		self.project_id = project_id
		self.language_code = language_code
		
		self.connect_session(session_id=session_id)
		self.parent = self.intents_client.project_agent_path(self.project_id)
		
	def connect_session(self, session_id=None):
		if session_id == None:
			session_id = str(uuid.uuid4())
		self.session_id = session_id
		self.session = self.session_client.session_path(project=self.project_id,
														session=self.session_id)
		print('Session path: {}\n'.format(self.session))

	def detect_intent_text(self, text):
		"""Returns the result of detect intent with texts as inputs.
		Using the same `session_id` between requests allows continuation
		of the conversation."""

		text_input = dialogflow.types.TextInput(text=text, language_code=self.language_code)
		query_input = dialogflow.types.QueryInput(text=text_input)

		response = self.session_client.detect_intent(session=self.session, query_input=query_input)
		#print(response)
		print('=' * 20)
		print('Query text: {}'.format(response.query_result.query_text))
		print('Detected intent: {} (confidence: {})\n'.format(
			response.query_result.intent.display_name,
			response.query_result.intent_detection_confidence))
		print('Fulfillment text: {}\n'.format(
			response.query_result.fulfillment_text))
		print('=' * 20)
		
		return response
		
		
	def list_intents(self):
		intents = self.intents_client.list_intents(self.parent)

		for intent in intents:
			print('=' * 20)
			print('Intent name: {}'.format(intent.name))
			print('Intent display_name: {}'.format(intent.display_name))
			print('Action: {}\n'.format(intent.action))
			print('Root followup intent: {}'.format(
				intent.root_followup_intent_name))
			print('Parent followup intent: {}\n'.format(
				intent.parent_followup_intent_name))

			print('Input contexts:')
			for input_context_name in intent.input_context_names:
				print('\tName: {}'.format(input_context_name))

			print('Output contexts:')
			for output_context in intent.output_contexts:
				print('\tName: {}'.format(output_context.name))
		return intents
		
	def create_intent(self, display_name, training_phrases_parts, message_texts):
		
		training_phrases = []
		for training_phrases_part in training_phrases_parts:
			part = dialogflow.types.Intent.TrainingPhrase.Part(
				text=training_phrases_part)
			# Here we create a new training phrase for each provided part.
			training_phrase = dialogflow.types.Intent.TrainingPhrase(parts=[part])
			training_phrases.append(training_phrase)

		text = dialogflow.types.Intent.Message.Text(text=message_texts)
		message = dialogflow.types.Intent.Message(text=text)

		intent = dialogflow.types.Intent(
			display_name=display_name,
			training_phrases=training_phrases,
			messages=[message])

		response = self.intents_client.create_intent(self.parent, intent)

		print('Intent created: {}'.format(response))
		return response
	
	# [START dialogflow_delete_intent]
	def delete_intent(self, intent_id):
		intent_path = self.intents_client.intent_path(self.project_id, intent_id)

		self.intents_client.delete_intent(intent_path)
	# [END dialogflow_delete_intent]


	# Helper to get intent from display name.
	def _get_intent_ids(self, display_name):
		intents = self.intents_client.list_intents(self.parent)
		intent_names = [
			intent.name for intent in intents
			if intent.display_name == display_name]

		intent_ids = [
			intent_name.split('/')[-1] for intent_name
			in intent_names]
		
		return intent_ids

	
	def list_entities(self, entity_type_id):
		entity_type_path = self.entity_types_client.entity_type_path(self.project_id, entity_type_id)
		entities = self.entity_types_client.get_entity_type(entity_type_path).entities

		for entity in entities:
			print('Entity value: {}'.format(entity.value))
			print('Entity synonyms: {}\n'.format(entity.synonyms))
			
		return entities
	
	# [START dialogflow_create_entity]
	def create_entity(self, entity_type_id, entity_value, synonyms):
		"""Create an entity of the given entity type."""
		# Note: synonyms must be exactly [entity_value] if the
		# entity_type's kind is KIND_LIST
		synonyms = synonyms or [entity_value]

		entity_type_path = self.entity_types_client.entity_type_path(
			self.project_id, entity_type_id)

		entity = dialogflow.types.EntityType.Entity()
		entity.value = entity_value
		entity.synonyms.extend(synonyms)

		response = self.entity_types_client.batch_create_entities(
			entity_type_path, [entity])

		print('Entity created: {}'.format(response))
	# [END dialogflow_create_entity]


	# [START dialogflow_delete_entity]
	def delete_entity(self, entity_type_id, entity_value):
		"""Delete entity with the given entity type and entity value."""
		entity_type_path = self.entity_types_client.entity_type_path(
			self.project_id, entity_type_id)

		self.entity_types_client.batch_delete_entities(
			entity_type_path, [entity_value])
	# [END dialogflow_delete_entity]
	
	def list_entity_types(self):

		entity_types = self.entity_types_client.list_entity_types(self.parent)

		for entity_type in entity_types:
			print('Entity type name: {}'.format(entity_type.name))
			print('Entity type display name: {}'.format(entity_type.display_name))
			print('Number of entities: {}\n'.format(len(entity_type.entities)))
		return entity_types


	# [START dialogflow_create_entity_type]
	def create_entity_type(self, display_name, kind):
		"""Create an entity type with the given display name."""
		entity_type = dialogflow.types.EntityType(
			display_name=display_name, kind=kind)

		response = self.entity_types_client.create_entity_type(self.parent, entity_type)

		print('Entity type created: \n{}'.format(response))
	# [END dialogflow_create_entity_type]


	# [START dialogflow_delete_entity_type]
	def delete_entity_type(self, entity_type_id):
		"""Delete entity type with the given entity type name."""

		entity_type_path = self.entity_types_client.entity_type_path(
			project_id, entity_type_id)

		self.entity_types_client.delete_entity_type(entity_type_path)
	# [END dialogflow_delete_entity_type]


	# Helper to get entity_type_id from display name.
	def _get_entity_type_ids(self, display_name):
		entity_types = self.entity_types_client.list_entity_types(self.parent)
		entity_type_names = [
			entity_type.name for entity_type in entity_types
			if entity_type.display_name == display_name]

		entity_type_ids = [
			entity_type_name.split('/')[-1] for entity_type_name
			in entity_type_names]

		return entity_type_ids
	
	
	def list_session_entity_types(self):
		session_entity_types = (
			self.session_entity_types_client.
			list_session_entity_types(self.session))

		print('SessionEntityTypes for session {}:\n'.format(self.session))
		for session_entity_type in session_entity_types:
			print('\tSessionEntityType name: {}'.format(session_entity_type.name))
			print('\tNumber of entities: {}\n'.format(
				len(session_entity_type.entities)))
		return session_entity_types


	# [START dialogflow_create_session_entity_type]
	def create_session_entity_type(self, entity_values, entity_type_display_name, entity_override_mode):
		"""Create a session entity type with the given display name."""
		session_entity_type_name = (
			self.session_entity_types_client.session_entity_type_path(
				self.project_id, self.session_id, entity_type_display_name))

		# Here we use the entity value as the only synonym.
		entities = [
			dialogflow.types.EntityType.Entity(value=value, synonyms=[value])
			for value in entity_values]
		session_entity_type = dialogflow.types.SessionEntityType(
			name=session_entity_type_name,
			entity_override_mode=entity_override_mode,
			entities=entities)

		response = self.session_entity_types_client.create_session_entity_type(
			self.session, session_entity_type)

		print('SessionEntityType created: \n\n{}'.format(response))
	# [END dialogflow_create_session_entity_type]


	# [START dialogflow_delete_session_entity_type]
	def delete_session_entity_type(self, entity_type_display_name):
		"""Delete session entity type with the given entity type display name."""

		session_entity_type_name = (
			self.session_entity_types_client.session_entity_type_path(
				self.project_id, self.session_id, entity_type_display_name))

		self.session_entity_types_client.delete_session_entity_type(
			session_entity_type_name)
	# [END dialogflow_delete_session_entity_type]
		
		

if __name__ == '__main__':
	engine = DialogflowEngine()
	print(engine.detect_intent_text("Hello there"))
	print(engine.detect_intent_text("Bye"))
	print(engine.list_intents())
	print(engine.list_entity_types())
	engine.list_session_entity_types()
	
	
	