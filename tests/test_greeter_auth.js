const {test} = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const source = fs.readFileSync(path.join(__dirname, '../share/greeter/Auth.js'), 'utf8');

function fixture() {
    const context = vm.createContext({});
    vm.runInContext(source, context);
    const calls = [];
    let state;
    const backend = Object.fromEntries(['createSession', 'respond', 'launch', 'cancelSession']
        .map(name => [name, (...args) => calls.push([name, ...args])]));
    const auth = context.create(backend, next => { state = next; });
    return {auth, calls, get state() { return state; }};
}

test('responds only when PAM requests a secret, then launches exactly once', () => {
    const f = fixture();
    f.auth.submit(' alice ', 'first-secret');
    assert.deepEqual(f.calls, [['createSession', 'alice']]);
    f.auth.message('Authenticating', false, false, false);
    assert.equal(f.calls.length, 1);
    f.auth.message('Password:', false, true, false);
    assert.deepEqual(f.calls[1], ['respond', 'first-secret']);
    f.auth.ready();
    f.auth.ready();
    assert.deepEqual(f.calls.slice(2), [['launch']]);
    assert.equal(f.state.busy, true);
});

test('additional secret challenges require a fresh response', () => {
    const f = fixture();
    f.auth.submit('alice', 'password');
    f.auth.message('Password:', false, true, false);
    f.auth.message('Verification code:', false, true, false);
    assert.equal(f.state.waiting, true);
    assert.equal(f.state.busy, false);
    assert.equal(f.calls.length, 2);
    f.auth.submit('alice', '123456');
    assert.deepEqual(f.calls[2], ['respond', '123456']);
});

test('does not submit a password to a visible PAM prompt', () => {
    const f = fixture();
    f.auth.submit('alice', 'do-not-echo');
    f.auth.message('Enter account:', false, true, true);
    assert.equal(f.calls.length, 1);
    assert.equal(f.state.echo, true);
    f.auth.submit('alice', 'account-name');
    assert.deepEqual(f.calls[1], ['respond', 'account-name']);
    f.auth.message('Password:', false, true, false);
    assert.equal(f.calls.length, 2);
    assert.equal(f.state.echo, false);
});

test('blocks duplicate submissions while a request is outstanding', () => {
    const f = fixture();
    f.auth.submit('alice', 'one');
    f.auth.submit('alice', 'two');
    assert.equal(f.calls.length, 1);
});

test('failed authentication allows retry with no stale password reuse', () => {
    const f = fixture();
    f.auth.submit('alice', 'wrong');
    f.auth.failure('Try again');
    assert.equal(f.state.error, true);
    assert.equal(f.state.busy, false);
    f.auth.submit('bob', 'new');
    f.auth.message('Password:', false, true, false);
    assert.deepEqual(f.calls, [['createSession', 'alice'], ['createSession', 'bob'], ['respond', 'new']]);
});

test('cancellation discards challenges and cannot launch a late success', () => {
    const f = fixture();
    f.auth.submit('alice', 'discard');
    f.auth.cancel();
    f.auth.message('Password:', false, true, false);
    f.auth.ready();
    f.auth.submit('bob', 'blocked');
    assert.deepEqual(f.calls, [['createSession', 'alice'], ['cancelSession']]);
    f.auth.inactive();
    assert.equal(f.state.busy, false);
    f.auth.submit('bob', 'fresh');
    f.auth.message('Password:', false, true, false);
    assert.deepEqual(f.calls.slice(2), [['createSession', 'bob'], ['respond', 'fresh']]);
});

test('refuses an empty username without contacting greetd', () => {
    const f = fixture();
    f.auth.submit('  ', 'anything');
    assert.equal(f.calls.length, 0);
    assert.equal(f.state.error, true);
});

test('an inactive or canceled session ignores unsolicited prompts', () => {
    const f = fixture();
    f.auth.message('Password:', false, true, false);
    f.auth.ready();
    assert.equal(f.calls.length, 0);
});
