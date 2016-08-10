#!/usr/bin/env python3
""" Usage: puppet-trigger.py <host>...

Arguments:
    TEXT  Message to be printed

Options:
    host1 host2...

"""
from docopt import docopt
import requests
import pika


def rest_queue_list(user, password, host, port=15672, virtual_host=None):
    """ fetch rabbitMQ queues """
    url = 'http://{}:{}/api/queues/{}'.format(host, port, virtual_host or '')
    response = requests.get(url, auth=(user, password))
    rabbitqueues = [q['name'] for q in response.json()]
    return rabbitqueues


if __name__ == '__main__':

    # ToDo: use external file to read paramters
    ARGS = docopt(__doc__)
    MSG = 'puppet'
    rabbituser = 'puppet'
    rabbitpassword = 'secretepass'
    rabbithost = 'puppethost.domain.com'

    for puppethost in ARGS['<host>']:
        queue = 'puppet-{}'.format(puppethost)
        credentials = pika.PlainCredentials(rabbituser, rabbitpassword)
        queues = rest_queue_list(rabbituser, rabbitpassword, rabbithost)
        if queue in queues:
            conn = pika.BlockingConnection(pika.ConnectionParameters(
                host=rabbithost, credentials=credentials))
            chan = conn.channel()
            chan.queue_declare(queue=queue, durable=True)
            chan.basic_publish(exchange='',
                               routing_key=queue,
                               body=MSG,
                               properties=pika.BasicProperties(
                                   delivery_mode=2,))
        else:
            print('queue {} does not exist'.format(queue))
