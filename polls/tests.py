import factory
from django.test import TestCase
from rest_framework.reverse import reverse

from polls.models import Choice, Poll, Participant


class PollFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Poll


class ChoiceFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Choice


class ParticipantFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Participant


class PollDeleteTest(TestCase):

    def setUp(self):
        self.ip = '192.64.4.52'
        creator = ParticipantFactory(ip=self.ip)
        self.poll = PollFactory(title='Do you believe in Python?', creator=creator)

    def test_delete(self):
        response = self.client.delete(
            reverse('poll-detail', args=(self.poll.id,)),
            REMOTE_ADDR=self.ip,
        )
        self.assertEqual(response.status_code, 204)
        self.assertEqual(Poll.objects.count(), 0)

    def test_delete_with_invalid_ip(self):
        response = self.client.delete(reverse('poll-detail', args=(self.poll.id,)))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(Poll.objects.count(), 1)

    def test_delete_with_invalid_id(self):
        response = self.client.delete(
            reverse('poll-detail', args=('invalid_id',)),
            REMOTE_ADDR=self.ip,
        )
        self.assertEqual(response.status_code, 404)
        self.assertEqual(Poll.objects.count(), 1)


class PollDetailTest(TestCase):

    def setUp(self):
        creator = ParticipantFactory(ip='192.64.4.52')
        participant = ParticipantFactory(ip='168.32.44.52')
        self.poll = PollFactory(
            title='Do you believe in Python?', creator=creator, multi_selection=True,
        )
        self.choice1 = ChoiceFactory(poll=self.poll, choice='May the Force be with you')
        self.choice1.participants.set([participant])
        self.choice2 = ChoiceFactory(poll=self.poll, choice='Always')

    def test_poll_detail_with_invalid_id(self):
        response = self.client.get(reverse('poll-detail', args=('invalid_id',)))
        self.assertEqual(response.status_code, 404)

    def test_poll_detail(self):
        expected_raw = {
            'id': str(self.poll.id),
            'title': 'Do you believe in Python?',
            'choices': [
                {
                    'choice': 'May the Force be with you', 'votes': 1,
                    'id': str(self.choice1.id),
                },
                {
                    'choice': 'Always', 'votes': 0, 'id': str(self.choice2.id),
                }
            ],
            'link': f'http://testserver/v1/polls/{self.poll.id}/',
            'created_at': str(self.poll.created_at.isoformat()).replace('+00:00', 'Z'),
            'multi_selection': True,
        }

        response = self.client.get(reverse('poll-detail', args=(self.poll.id,)))
        self.assertEqual(response.json(), expected_raw)
        self.assertEqual(response.status_code, 200)


class PollCreateTest(TestCase):

    def setUp(self):
        self.payload = {
            'title': 'Who is awesome?',
            'choices': [
                'Chuck Norris', 'Elon Musk', 'Jeff Bezos',
            ],
            'multi_selection': True,
        }

    def test_create_with_invalid_payload(self):
        response = self.client.post(reverse('poll-list'), data={})
        self.assertEqual(response.status_code, 400)

    def test_create(self):
        response = self.client.post(reverse('poll-list'), self.payload)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Poll.objects.count(), 1)
        self.assertTrue(Poll.objects.get().multi_selection)
        self.assertEqual(Choice.objects.count(), 3)
        self.assertEqual(Participant.objects.count(), 1)

        participant = Participant.objects.get()
        poll = Poll.objects.get()
        self.assertEqual(poll.creator, participant)


class PollVoteTest(TestCase):

    def setUp(self):
        creator = ParticipantFactory(ip='192.64.4.52')
        participant = ParticipantFactory(ip='168.32.44.52')
        self.poll = PollFactory(
            title='Do you believe in Python?', creator=creator, multi_selection=True,
        )
        self.choice1 = ChoiceFactory(poll=self.poll, choice='May the Force be with you')
        self.choice1.participants.set([participant])
        self.choice2 = ChoiceFactory(poll=self.poll, choice='Always')

    def test_vote_with_invalid_poll(self):
        response = self.client.post(reverse('poll-vote', args=('invalid_id',)), {})
        self.assertEqual(response.status_code, 404)

    def test_vote_with_invalid_data(self):
        response = self.client.post(reverse('poll-vote', args=(self.poll.id,)), {})
        self.assertEqual(response.status_code, 400)

    def test_vote(self):
        expected_raw = {
            'id': str(self.poll.id),
            'title': 'Do you believe in Python?',
            'choices': [
                {
                    'choice': 'May the Force be with you', 'votes': 2,
                    'id': str(self.choice1.id),
                },
                {
                    'choice': 'Always', 'votes': 1, 'id': str(self.choice2.id),
                }
            ],
            'link': f'http://testserver/v1/polls/{self.poll.id}/',
            'created_at': str(self.poll.created_at.isoformat()).replace('+00:00', 'Z'),
            'multi_selection': True,
        }

        payload = {'choices_id': [str(self.choice1.id), str(self.choice2.id)]}
        response = self.client.post(reverse('poll-vote', args=(self.poll.id,)), payload)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), expected_raw)

    def test_vote_with_invalid_choices(self):
        payload = {'choices_id': [str(self.choice1.id), 'f9999d18-23d0-4f50-a459-6dfa3e1069fb']}
        response = self.client.post(reverse('poll-vote', args=(self.poll.id,)), payload)

        self.assertEqual(response.status_code, 200)

    def test_vote_without_multi_selection(self):
        self.poll.multi_selection = False
        self.poll.save()
        payload = {'choices_id': [str(self.choice1.id), str(self.choice2.id)]}

        response = self.client.post(reverse('poll-vote', args=(self.poll.id,)), payload)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {'choices_id': ['multiple choices are not available']})


class PollSearchTest(TestCase):

    def setUp(self):
        creator = ParticipantFactory(ip='192.64.4.52')
        participant = ParticipantFactory(ip='168.32.44.52')
        self.poll = PollFactory(
            title='Do you believe in Python?', creator=creator, multi_selection=True,
        )
        self.choice1 = ChoiceFactory(poll=self.poll, choice='May the Force be with you')
        self.choice1.participants.set([participant])
        self.choice2 = ChoiceFactory(poll=self.poll, choice='Always')

    def test_poll_search(self):
        response = self.client.get(reverse('poll-list'), {'search': 'you believe'})
        self.assertEqual(response.json()[0]['id'], str(self.poll.id))
        self.assertEqual(response.status_code, 200)

    def test_poll_search_without_query(self):
        response = self.client.get(reverse('poll-list'))
        self.assertEqual(response.json()[0]['id'], str(self.poll.id))
        self.assertEqual(response.status_code, 200)
