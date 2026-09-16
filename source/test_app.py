import json
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from server import make_server


class InvitationFlowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.server = make_server('127.0.0.1', 0, self.temp.name + '/test.sqlite3')
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = 'http://127.0.0.1:' + str(self.server.server_port)

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join()
        self.temp.cleanup()

    def call(self, path, payload=None):
        data = None if payload is None else json.dumps(payload).encode()
        request = Request(self.base + path, data=data,
                          headers={'Content-Type': 'application/json'})
        try:
            with urlopen(request) as response:
                return response.status, json.load(response)
        except HTTPError as response:
            with response:
                return response.code, json.load(response)

    def demo(self, scenario='priority'):
        status, result = self.call('/api/demos', {'scenario': scenario})
        self.assertEqual(status, 201)
        return result

    def test_invitation_confirmation_reaches_organizer_without_payment(self):
        owner = self.demo()
        jordan = next(i for i in owner['invitations'] if i['name'] == 'Jordan')
        status, guest = self.call('/api/view/' + jordan['token'])
        self.assertEqual(status, 200)
        self.assertEqual(guest['viewer']['status'], 'invited')
        status, confirmed = self.call('/api/confirm/' + jordan['token'], {})
        self.assertEqual(status, 200)
        self.assertEqual(confirmed['viewer']['status'], 'confirmed')
        self.assertFalse(confirmed['viewer']['paid'])
        _, refreshed = self.call('/api/view/' + owner['token'])
        self.assertEqual(len(refreshed['players']), 3)
        self.assertIn('Jordan', [p['name'] for p in refreshed['players']])

    def test_wider_circle_cannot_claim_during_first_dibs(self):
        owner = self.demo()
        casey = next(i for i in owner['invitations'] if i['name'] == 'Casey')
        status, result = self.call('/api/confirm/' + casey['token'], {})
        self.assertEqual(status, 403)
        self.assertIn('first dibs', result['error'])

    def test_original_preferred_invitation_still_works_after_first_dibs(self):
        owner = self.demo('wider')
        for name in ('Casey', 'Jordan'):
            guest = next(i for i in owner['invitations'] if i['name'] == name)
            status, result = self.call('/api/confirm/' + guest['token'], {})
            self.assertEqual(status, 200)
            self.assertEqual(result['viewer']['status'], 'confirmed')

    def test_only_one_of_two_simultaneous_claims_gets_last_spot(self):
        owner = self.demo('last-spot')
        self.assertEqual(len(owner['players']), 3)
        tokens = [i['token'] for i in owner['invitations'] if i['name'] in ('Riley', 'Casey')]
        with ThreadPoolExecutor(max_workers=2) as pool:
            results = list(pool.map(lambda token: self.call('/api/confirm/' + token, {}), tokens))
        self.assertEqual(sorted(status for status, _ in results), [200, 409])
        _, state = self.call('/api/view/' + owner['token'])
        self.assertEqual(len(state['players']), 4)

    def test_duplicate_confirmation_does_not_consume_another_spot(self):
        owner = self.demo()
        token = next(i['token'] for i in owner['invitations'] if i['name'] == 'Jordan')
        for _ in range(2):
            status, _ = self.call('/api/confirm/' + token, {})
            self.assertEqual(status, 200)
        _, state = self.call('/api/view/' + owner['token'])
        self.assertEqual(len(state['players']), 3)

    def test_guest_cannot_access_organizer_or_other_invitation_tokens(self):
        owner = self.demo()
        guest = next(i for i in owner['invitations'] if i['name'] == 'Jordan')
        _, result = self.call('/api/view/' + guest['token'])
        self.assertNotIn('invitations', result)
        self.assertNotIn(owner['token'], json.dumps(result))
        self.assertNotIn('paid', result['players'][0])

    def test_state_persists_when_store_is_reopened(self):
        from store import Store
        owner = self.demo()
        token = next(i['token'] for i in owner['invitations'] if i['name'] == 'Jordan')
        self.call('/api/confirm/' + token, {})
        reopened = Store(self.temp.name + '/test.sqlite3')
        self.assertEqual(len(reopened.view(owner['token'])['players']), 3)

    def test_bad_links_and_organizer_claims_fail_cleanly(self):
        self.assertEqual(self.call('/api/view/missing')[0], 404)
        self.assertEqual(self.call('/api/confirm/missing', {})[0], 404)
        self.assertEqual(self.call('/api/confirm/' + self.demo()['token'], {})[0], 403)

    def test_scenarios_are_isolated_and_invalid_scenarios_rejected(self):
        first, second = self.demo(), self.demo()
        token = next(i['token'] for i in first['invitations'] if i['name'] == 'Jordan')
        self.call('/api/confirm/' + token, {})
        _, state = self.call('/api/view/' + second['token'])
        self.assertEqual(len(state['players']), 2)
        self.assertEqual(self.call('/api/demos', {'scenario': 'unknown'})[0], 400)


if __name__ == '__main__':
    unittest.main()
