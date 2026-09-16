const button = document.querySelector('#action');
const list = document.querySelector('#player-list');
const friends = ['Tiger Woods', 'Rory McIlroy', 'Nelly Korda'];
let state = 'open';

function render() {
  const open = state === 'open';
  const full = state === 'full';
  document.querySelector('main').dataset.state = state;
  document.querySelector('#subtitle').textContent = open
    ? 'Your reservation is booked. Fill the other 3 spots.'
    : full ? 'Everyone’s in. See you on Saturday.' : 'Invitations sent. Waiting on 3 replies.';
  document.querySelector('#count').textContent = full ? '4 of 4 confirmed' : '1 of 4 confirmed';
  list.innerHTML = '<li><span class="player-avatar" aria-hidden="true">B</span><div class="player-name"><strong>Ben Pardee <span class="you">(you)</span></strong><small>Organizer</small></div><span class="player-status">✓ Confirmed</span></li>'
    + friends.map((name, i) => `<li><span class="player-avatar ${open ? 'open' : 'friend-'+i}" aria-hidden="true">${open ? '+' : name[0]}</span><div class="player-name"><strong>${open ? 'Open spot' : name}</strong><small>${open ? 'Invite a friend' : full ? 'Payment pending' : 'Awaiting their reply'}</small></div><span class="player-status ${open ? 'available' : full ? '' : 'pending'}">${open ? 'Available' : full ? '✓ Confirmed' : '◷ Pending'}</span></li>`).join('');
  button.textContent = open ? 'Invite 3 friends →' : full ? '✓ Group confirmed' : 'Nudge your friends';
  button.classList.toggle('confirmed', full);
  button.disabled = full;
  document.querySelector('#reassurance').textContent = open
    ? '3 spots are waiting to be filled.'
    : full ? 'All 4 spots filled. Friends can pay you later.' : 'A spot is confirmed when a friend accepts.';
}
button.onclick = () => {
  if (state === 'full') return;
  state = state === 'open' ? 'pending' : 'full';
  render();
};
render();

document.querySelector('#reset').onclick = (event) => {
  event.preventDefault();
  state = 'open';
  render();
  button.focus();
};
