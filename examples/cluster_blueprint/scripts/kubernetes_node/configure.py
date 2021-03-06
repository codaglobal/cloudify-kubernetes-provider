#!/usr/bin/env python

import subprocess
from cloudify import ctx
from cloudify.exceptions import NonRecoverableError, OperationRetry


def execute_command(_command):

    ctx.logger.debug('_command {0}.'.format(_command))

    subprocess_args = {
        'args': _command.split(),
        'stdout': subprocess.PIPE,
        'stderr': subprocess.PIPE
    }

    ctx.logger.debug('subprocess_args {0}.'.format(subprocess_args))

    process = subprocess.Popen(**subprocess_args)
    output, error = process.communicate()

    ctx.logger.debug('command: {0} '.format(_command))
    ctx.logger.debug('output: {0} '.format(output))
    ctx.logger.debug('error: {0} '.format(error))
    ctx.logger.debug('process.returncode: {0} '.format(process.returncode))

    if process.returncode:
        ctx.logger.error('Running `{0}` returns error.'.format(_command))
        return False

    return output


if __name__ == '__main__':

    # echo 1 | sudo tee /proc/sys/net/bridge/bridge-nf-call-iptables
    status = execute_command(
        "sudo sysctl net.bridge.bridge-nf-call-iptables=1")
    if status is False:
        raise OperationRetry('Failed to set bridge-nf-call-iptables')

    hostname = execute_command('hostname')
    ctx.instance.runtime_properties['hostname'] = hostname.rstrip('\n')

    # Get the master cluster info.
    masters = \
        [x for x in ctx.instance.relationships if
         x.target.instance.runtime_properties.get(
             'KUBERNETES_MASTER', False)]
    if len(masters) != 1:
        raise NonRecoverableError(
            'Currently, a Kubernetes node must have a '
            'dependency on one Kubernetes master.')
    master = masters[0]
    bootstrap_token = \
        master.target.instance.runtime_properties['bootstrap_token']
    bootstrap_hash = \
        master.target.instance.runtime_properties['bootstrap_hash']
    master_ip = \
        master.target.instance.runtime_properties['master_ip']
    master_port = \
        master.target.instance.runtime_properties['master_port']

    # Join the cluster.
    join_command = (
        'sudo kubeadm join --token {0} --discovery-token-ca-cert-hash {1} '
        '{2}:{3} --skip-preflight-checks'
        .format(bootstrap_token, bootstrap_hash, master_ip, master_port)
    )
    ctx.logger.info("Join by {}".format(repr(join_command)))
    execute_command(join_command)

    # Install weave-related utils
    execute_command('sudo curl -L git.io/weave -o /usr/local/bin/weave')
    execute_command('sudo chmod a+x /usr/local/bin/weave')
    execute_command('sudo curl -L git.io/scope -o /usr/local/bin/scope')
    execute_command('sudo chmod a+x /usr/local/bin/scope')
    execute_command('/usr/local/bin/scope launch')
