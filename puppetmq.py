#!/usr/bin/env python3
"""
  RabbitMQ Listener: trigger a puppet run
"""
import os
import socket
import logging
import subprocess as sp
import pika
from systemd.journal import JournalHandler


def log_handler(message, log_info='puppet-trigger'):
    """ send message to journal """
    log = logging.getLogger(log_info)
    log.addHandler(JournalHandler())
    log.setLevel(logging.INFO)
    log.info(message)


def callback(ch, method, properties, body):
    """ send SIGUSR1 to puppet process """
    body = body.decode()
    if body == 'puppet':
        puppet_cmd = ["/usr/bin/pkill", "-SIGUSR1", "-f", "bin/puppet agent"]
        proc_puppet = sp.Popen(puppet_cmd, stdout=sp.PIPE, stderr=sp.STDOUT)
        _ = proc_puppet.communicate()
        retcode = proc_puppet.returncode
        log_msg = 'SIGUSR1 sent to puppet and exited with status {}'.format(
            retcode)
        log_handler(log_msg)

    msg_body = 'acknowledging queue message with body {}'.format(body)
    log_handler(msg_body)
    ch.basic_ack(delivery_tag=method.delivery_tag)


if __name__ == "__main__":

    credentials = pika.PlainCredentials('puppet', 'puppet')
    rabbithost = 'shiva.flat.global'
    rabbitqueue = 'puppet-{}'.format(socket.gethostname())

    try:
        conn = pika.BlockingConnection(pika.ConnectionParameters(
            host=rabbithost,
            credentials=credentials))
        channel = conn.channel()
        channel.queue_declare(queue=rabbitqueue, durable=True)
        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(callback, queue=rabbitqueue)
    except Exception as err:
        print("PuppetMQ: Failed to create queue: {0}".format(err))
        os.sys.exit(1)

    MQ_MSG = "PuppetMQ: Starting consuming from puppet queue."
    log_handler(MQ_MSG)
    channel.start_consuming()
