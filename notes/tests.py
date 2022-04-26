from django.test import TestCase, Client
from notes.models import Note
from faker import Faker
import json

faker = Faker()


def generate_title(word_cnt=5):
    return ' '.join(faker.words(word_cnt))


def generate_content(para_cnt=5):
    return '\n'.join(faker.paragraphs(para_cnt))


def generate_note(title=None, content=None):
    title = generate_title() if title is None else title
    content = generate_content() if content is None else content
    return Note.objects.create(title=title, content=content)


def generate_notes(note_cnt=5):
    return [generate_note() for i in range(note_cnt)]


# serialize_note turns a note object to dict
def serialize_note(note):
    return {
        'id': note.id,
        'title': note.title,
        'content': note.content
    }


def serialize_notes(notes):
    return [serialize_note(note) for note in notes]


class ListNoteTestCase(TestCase):
    """
    ListNoteTestCase tests list function of the program
    URL: /notes/
    """
    def setUp(self):
        self.notes = generate_notes()
        self.client = Client(HTTP_ACCEPT='application/json')

    def test_list_notes(self):
        response = self.client.get('/notes/')
        expected_response = json.dumps(serialize_notes(self.notes))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), expected_response)


class CreateNoteTestCase(TestCase):
    """
    CreateNoteTestCase tests functions of creating notes
    URL: /notes/
    """
    def test_create_note(self):
        expected_note = {
            'title': ' '.join(faker.words(5)),
            'content': '\n'.join(faker.paragraphs(5))
        }
        response = self.client.post('/notes/', expected_note)
        self.assertEqual(response.status_code, 201)

        data = response.json()
        self.assertEqual(expected_note['title'], data['title'])
        self.assertEqual(expected_note['content'], data['content'])
        self.assertTrue('id' in data.keys())

        pk = data['id']
        self.assertTrue(Note.objects.filter(pk=pk).exists())

        note = Note.objects.get(pk=pk)
        self.assertEqual(expected_note['title'], note.title)
        self.assertEqual(expected_note['content'], note.content)


class ReadNoteTestCase(TestCase):
    """
    ReadNoteTestCase tests detail of a note can be returned
    URL: /notes/<int:pk>
    """
    def setUp(self):
        self.notes = generate_notes()
        self.note = self.notes[0]

    def test_read_note(self):
        expected_response = json.dumps(serialize_note(self.note))
        response = self.client.get('/notes/' + str(self.note.id))
        self.assertEqual(response.status_code, 200)

        data = response.json()
        serialized = serialize_note(self.note)
        for field in serialized.keys():
            self.assertEqual(data[field], serialized[field])


class UpdateNoteTestCase(TestCase):
    """
    UpdateNoteTestCase tests updating function of note
    URL: /notes/<int:pk>
    """
    def setUp(self):
        self.notes = generate_notes()
        self.note = self.notes[0]

    def test_update_note(self):
        patch_info = {
            'title': ' '.join(faker.words(5)),
            'content': '\n'.join(faker.paragraphs(5))
        }
        serialized_request = json.dumps(patch_info)
        response = self.client.patch('/notes/' + str(self.note.id), serialized_request)
        self.assertEqual(response.status_code, 200)

        patch_info['id'] = self.note.id
        data = response.json()
        for field in patch_info.keys():
            self.assertEqual(data[field], patch_info[field])

        note = Note.objects.get(pk=self.note.id)
        self.assertEqual(note.title, patch_info['title'])
        self.assertEqual(note.content, patch_info['content'])


class DeleteNoteTestCase(TestCase):
    """
    UpdateNoteTestCase tests updating function of note
    URL: /notes/<int:pk>
    """
    def setUp(self):
        self.notes = generate_notes()
        self.note = self.notes[0]

    def test_delete_note(self):
        response = self.client.delete('/notes/' + str(self.note.id))
        self.assertEqual(response.status_code, 204)
        self.assertFalse(Note.objects.filter(pk=self.note.id).exists())

