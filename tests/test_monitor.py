from __future__ import unicode_literals


def wait_for_command(client, monitor, command):
    # issue a command with a key name that's local to this process.
    # if we find a command with our key before the command we're waiting
    # for, something went wrong
    key = '__REDIS-PY-%s__' % str(client.client_id())
    client.get(key)
    while True:
        monitor_response = monitor.next_command()
        if command in monitor_response['command']:
            return monitor_response
        if key in monitor_response['command']:
            return None


class TestPipeline(object):
    def test_response_pieces(self, r):
        with r.monitor() as m:
            r.ping()
            response = wait_for_command(r, m, 'PING')
            assert isinstance(response['time'], float)
            assert response['db'] == 9
            assert isinstance(response['client_address'], str)
            assert isinstance(response['client_port'], str)
            assert response['command'] == 'PING'

    def test_command_with_quoted_key(self, r):
        with r.monitor() as m:
            r.get('foo"bar')
            response = wait_for_command(r, m, 'GET foo"bar')
            assert response['command'] == 'GET foo"bar'

    def test_wait_command_not_found(self, r):
        "Make sure the wait_for_command func works when command is not found"
        with r.monitor() as m:
            response = wait_for_command(r, m, 'nothing')
            assert response is None