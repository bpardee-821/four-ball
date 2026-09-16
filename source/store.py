"""Small, persistent demo store. Link tokens grant access to sample identities."""
import secrets
import sqlite3
from contextlib import contextmanager


class Problem(Exception):
    def __init__(self, status, message):
        self.status, self.message = status, message


class Store:
    def __init__(self, path):
        self.path = path
        with self.connection() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS rounds (
                    id TEXT PRIMARY KEY, owner TEXT UNIQUE, scenario TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS invitations (
                    token TEXT PRIMARY KEY, round_id TEXT NOT NULL,
                    name TEXT NOT NULL, audience TEXT NOT NULL,
                    status TEXT NOT NULL, paid INTEGER NOT NULL DEFAULT 0);
            ''')

    @contextmanager
    def connection(self):
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        try:
            with db:
                yield db
        finally:
            db.close()

    def create(self, scenario):
        if scenario not in ('priority', 'wider', 'last-spot'):
            raise Problem(400, 'Choose a supported demo scenario.')
        round_id, owner = secrets.token_urlsafe(24), secrets.token_urlsafe(24)
        with self.connection() as db:
            db.execute('INSERT INTO rounds VALUES (?, ?, ?)', (round_id, owner, scenario))
            for name, audience, status, paid in [
                ('Alex', 'organizer', 'confirmed', 1),
                ('Sam', 'preferred', 'confirmed', 0),
                ('Jordan', 'preferred', 'invited', 0),
                ('Riley', 'preferred', 'invited', 0),
                ('Casey', 'wider', 'invited', 0),
            ]:
                if scenario == 'last-spot' and name == 'Jordan':
                    status = 'confirmed'
                db.execute('INSERT INTO invitations VALUES (?, ?, ?, ?, ?, ?)',
                           (secrets.token_urlsafe(24), round_id, name, audience, status, paid))
        return self.view(owner)

    def identify(self, db, token):
        row = db.execute('SELECT * FROM rounds WHERE owner = ?', (token,)).fetchone()
        if row:
            return row, None
        guest = db.execute('SELECT * FROM invitations WHERE token = ?', (token,)).fetchone()
        if not guest:
            raise Problem(404, 'This invitation could not be found. Ask the organizer for a new link.')
        row = db.execute('SELECT * FROM rounds WHERE id = ?', (guest['round_id'],)).fetchone()
        return row, guest

    def view(self, token):
        with self.connection() as db:
            round_data, guest = self.identify(db, token)
            invitations = [dict(row) for row in db.execute(
                'SELECT * FROM invitations WHERE round_id = ? ORDER BY rowid', (round_data['id'],))]
        result = {'token': token, 'role': 'guest' if guest else 'organizer',
                  'scenario': round_data['scenario'], 'capacity': 4,
                  'players': [{k: p[k] for k in (('name', 'audience') if guest else ('name', 'audience', 'paid'))}
                              for p in invitations if p['status'] == 'confirmed']}
        if guest:
            result['viewer'] = {k: guest[k] for k in ('name', 'audience', 'status', 'paid')}
        else:
            result['invitations'] = invitations
        return result

    def confirm(self, token):
        with self.connection() as db:
            db.execute('BEGIN IMMEDIATE')
            round_data, guest = self.identify(db, token)
            if guest is None:
                raise Problem(403, 'Use a player invitation to confirm a spot.')
            if guest['status'] != 'confirmed':
                if guest['audience'] == 'wider' and round_data['scenario'] == 'priority':
                    raise Problem(403, 'Preferred friends still have first dibs. Check with Alex before joining.')
                count = db.execute("SELECT count(*) FROM invitations WHERE round_id = ? AND status = 'confirmed'",
                                   (round_data['id'],)).fetchone()[0]
                if count >= 4:
                    raise Problem(409, 'The last spot has been taken. You have not been added or charged.')
                db.execute("UPDATE invitations SET status = 'confirmed' WHERE token = ?", (token,))
        return self.view(token)
