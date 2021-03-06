#!/usr/bin/python

from flask import Flask, render_template, request, jsonify
from kvirt.config import Kconfig
from kvirt.defaults import TEMPLATES
from kvirt import dockerutils
from kvirt import nameutils
import os

app = Flask(__name__)
try:
    app.config.from_object('settings')
    config = app.config
except ImportError:
    config = {'PORT': os.environ.get('PORT', 9000)}

debug = config['DEBUG'] if 'DEBUG' in config.keys() else True
port = int(config['PORT']) if 'PORT'in config.keys() else 9000


# VMS


@app.route("/")
@app.route('/vms')
def vms():
    """
    retrieves all vms
    """
    config = Kconfig()
    k = config.k
    reportdir = config.reportdir
    vms = []
    for vm in k.list():
        name = vm[0]
        if os.path.exists('%s/%s.txt' % (reportdir, name)):
            if os.path.exists('%s/%s.running' % (reportdir, name)):
                vm[6] = 'Running'
            else:
                vm[6] = 'OK'
        # sshcommand = k.ssh(name, tunnel=config.tunnel, insecure=config.insecure)
        # if sshcommand is None:
        #     sshcommand = ''
        # vm.append(sshcommand)
        vms.append(vm)
    return render_template('vms.html', title='Home', vms=vms, client=config.client)


@app.route('/vmcreate')
def vmcreate():
    """
    create vm
    """
    config = Kconfig()
    profiles = config.list_profiles()
    return render_template('vmcreate.html', title='CreateVm', profiles=profiles, client=config.client)


@app.route('/vmprofiles')
def vmprofiles():
    """
    retrieves vm profiles
    """
    config = Kconfig()
    profiles = config.list_profiles()
    return render_template('vmprofiles.html', title='VmProfiles', profiles=profiles, client=config.client)


@app.route("/diskaction", methods=['POST'])
def diskaction():
    """
    add/delete disk to vm
    """
    config = Kconfig()
    k = config.k
    if 'action' in request.form:
        action = request.form['action']
        if action == 'add':
            name = request.form['name']
            size = int(request.form['size'])
            pool = request.form['pool']
            result = k.add_disk(name, size, pool)
        elif action == 'delete':
            name = request.form['name']
            diskname = request.form['disk']
            result = k.delete_disk(name, diskname)
        response = jsonify(result)
        print(response)
        response.status_code = 200
    else:
        failure = {'result': 'failure', 'reason': "Invalid Data"}
        response = jsonify(failure)
        response.status_code = 400
    return response


@app.route("/nicaction", methods=['POST'])
def nicaction():
    """
    add/delete nic to vm
    """
    config = Kconfig()
    k = config.k
    if 'action' in request.form:
        action = request.form['action']
        if action == 'add':
            name = request.form['name']
            network = request.form['network']
            result = k.add_nic(name, network)
        elif action == 'delete':
            name = request.form['name']
            nicname = request.form['nic']
            result = k.delete_nic(name, nicname)
        response = jsonify(result)
        print(response)
        response.status_code = 200
    else:
        failure = {'result': 'failure', 'reason': "Invalid Data"}
        response = jsonify(failure)
        response.status_code = 400
    return response


# CONTAINERS


@app.route('/containercreate')
def containercreate():
    """
    create container
    """
    config = Kconfig()
    profiles = config.list_containerprofiles()
    return render_template('containercreate.html', title='CreateContainer', profiles=profiles, client=config.client)


# POOLS


@app.route('/poolcreate')
def poolcreate():
    """
    pool form
    """
    config = Kconfig()
    return render_template('poolcreate.html', title='CreatePool', client=config.client)


@app.route("/poolaction", methods=['POST'])
def poolaction():
    """
    create/delete pool
    """
    config = Kconfig()
    k = config.k
    if 'pool' in request.form:
        pool = request.form['pool']
        action = request.form['action']
        if action == 'create':
            path = request.form['path']
            pooltype = request.form['type']
            print pool, path, pooltype
            result = k.create_pool(name=pool, poolpath=path, pooltype=pooltype)
            print(result)
        elif action == 'delete':
            result = k.delete_pool(name=pool)
        else:
            result = "Nothing to do"
        response = jsonify(result)
        print(response)
        response.status_code = 200
    else:
        failure = {'result': 'failure', 'reason': "Invalid Data"}
        response = jsonify(failure)
        response.status_code = 400
    return response

# NETWORKS


@app.route('/networkcreate')
def networkcreate():
    """
    network form
    """
    config = Kconfig()
    return render_template('networkcreate.html', title='CreateNetwork', client=config.client)


@app.route("/networkaction", methods=['POST'])
def networkaction():
    """
    create/delete network
    """
    config = Kconfig()
    k = config.k
    if 'network' in request.form:
        network = request.form['network']
        action = request.form['action']
        if action == 'create':
            cidr = request.form['cidr']
            dhcp = bool(request.form['dhcp'])
            isolated = bool(request.form['isolated'])
            nat = not isolated
            print(network, cidr, dhcp, nat)
            result = k.create_network(name=network, cidr=cidr, dhcp=dhcp, nat=nat)
        elif action == 'delete':
            result = k.delete_network(name=network)
        else:
            result = "Nothing to do"
        response = jsonify(result)
        print(response)
        response.status_code = 200
        return response
    else:
        failure = {'result': 'failure', 'reason': "Invalid Data"}
        response = jsonify(failure)
        response.status_code = 400
        return jsonify(failure)


# PLANS


@app.route('/plancreate')
def plancreate():
    """
    create plan
    """
    config = Kconfig()
    return render_template('plancreate.html', title='CreateNetwork', client=config.client)


@app.route("/vmaction", methods=['POST'])
def vmaction():
    """
    start/stop/delete/create vm
    """
    config = Kconfig()
    k = config.k
    if 'name' in request.form:
        name = request.form['name']
        action = request.form['action']
        if action == 'start':
            result = k.start(name)
        elif action == 'stop':
            result = k.stop(name)
        elif action == 'delete':
            result = k.delete(name)
        elif action == 'create' and 'profile' in request.form:
            profile = request.form['profile']
            result = config.create_vm(name, profile)
        else:
            result = "Nothing to do"
        print(result)
        response = jsonify(result)
        print(response)
        response.status_code = 200
        return response
    else:
        failure = {'result': 'failure', 'reason': "Invalid Data"}
        response = jsonify(failure)
        response.status_code = 400
        return jsonify(failure)


# HOSTS

@app.route("/hostaction", methods=['POST'])
def hostaction():
    """
    enable/disable/default host
    """
    config = Kconfig()
    if 'name' in request.form:
        name = request.form['name']
        action = request.form['action']
        if action == 'enable':
            result = config.handle_host(enable=name)
        elif action == 'disable':
            result = config.handle_host(disable=name)
        elif action == 'switch':
            result = config.handle_host(switch=name)
        else:
            result = "Nothing to do"
        response = jsonify(result)
        response.status_code = 200
        return response
    else:
        failure = {'result': 'failure', 'reason': "Invalid Data"}
        response = jsonify(failure)
        response.status_code = 400
        return jsonify(failure)


@app.route("/snapshotaction", methods=['POST'])
def snapshotaction():
    """
    create/delete/revert snapshot
    """
    config = Kconfig()
    k = config.k
    if 'name' in request.form:
        name = request.form['name']
        action = request.form['action']
        if action == 'list':
            result = k.snapshot(None, name, listing=True)
        elif action == 'create':
            snapshot = request.form['snapshot']
            result = k.snapshot(snapshot, name)
        elif action == 'delete':
            snapshot = request.form['snapshot']
            result = k.snapshot(snapshot, name, delete=True)
        elif action == 'revert':
            snapshot = request.form['snapshot']
            name = request.form['name']
            result = k.snapshot(snapshot, name, revert=True)
        print(result)
        response = jsonify(result)
        print(response)
        response.status_code = 200
        return response
    else:
        failure = {'result': 'failure', 'reason': "Invalid Data"}
        response = jsonify(failure)
        response.status_code = 400
        return jsonify(failure)


@app.route("/planaction", methods=['POST'])
def planaction():
    """
    start/stop/delete plan
    """
    config = Kconfig()
    if 'name' in request.form:
        plan = request.form['name']
        action = request.form['action']
        if action == 'start':
            result = config.plan(plan, start=True)
        elif action == 'stop':
            result = config.plan(plan, stop=True)
        elif action == 'delete':
            result = config.plan(plan, delete=True)
        elif action == 'create':
            url = request.form['url']
            planfile = request.form['planfile']
            if url.endswith('.yml'):
                planfile = os.path.basename(url)
                url = os.path.dirname(url)
            deploy = request.form['deploy']
            if deploy == 'on':
                deploy = True
            else:
                deploy = False
            if plan == '':
                plan = nameutils.get_random_name()
            # path = request.form['path']
            result = config.plan(plan, get=url, path=plan, inputfile=planfile)
            if deploy:
                result = config.plan(plan, inputfile="%s/%s" % (plan, planfile))
        else:
            result = "Nothing to do"
        print(result)
        response = jsonify(result)
        print(response)
        response.status_code = 200
        return response
    else:
        failure = {'result': 'failure', 'reason': "Invalid Data"}
        response = jsonify(failure)
        response.status_code = 400


@app.route("/report", methods=['POST'])
def report():
    """
    updatestatus
    """
    config = Kconfig()
    k = config.k
    reportdir = config.reportdir
    if 'name' in request.form and 'report' in request.form and 'status' in request.form:
        name = request.form['name']
        status = request.form['status']
        report = request.form['report']
    if not k.exists(name):
        return "KO"
    k.update_metadata(name, 'report', status)
    if not os.path.exists(reportdir):
        os.mkdir(reportdir)
    with open("%s/%s.txt" % (reportdir, name), 'w') as f:
        f.write(report)
    print("Name: %s Status: %s" % (name, status))
    if status == 'Running' and not os.path.exists("%s/%s.running" % (reportdir, name)):
        open("%s/%s.running" % (reportdir, name), 'a').close()
    if status == 'OK' and os.path.exists("%s/%s.running" % (reportdir, name)):
        os.remove("%s/%s.running" % (reportdir, name))
    return 'OK'


@app.route('/containers')
def containers():
    """
    retrieves all containers
    """
    config = Kconfig()
    k = config.k
    containers = dockerutils.list_containers(k)
    return render_template('containers.html', title='Containers', containers=containers, client=config.client)


@app.route('/networks')
def networks():
    """
    retrieves all networks
    """
    config = Kconfig()
    k = config.k
    networks = k.list_networks()
    return render_template('networks.html', title='Networks', networks=networks, client=config.client)


@app.route('/pools')
def pools():
    """
    retrieves all pools
    """
    config = Kconfig()
    k = config.k
    pools = []
    for pool in k.list_pools():
        poolpath = k.get_pool_path(pool)
        pools.append([pool, poolpath])
    return render_template('pools.html', title='Pools', pools=pools, client=config.client)


@app.route('/hosts')
def hosts():
    """
    retrieves all hosts
    """
    config = Kconfig()
    clients = []
    for client in sorted(config.clients):
        enabled = config.ini[client].get('enabled', True)
        if client == config.client:
            clients.append([client, enabled, 'X'])
        else:
            clients.append([client, enabled, ''])
    print clients
    return render_template('hosts.html', title='Hosts', clients=clients, client=config.client)


@app.route('/plans')
def plans():
    """
    retrieves all plans
    """
    config = Kconfig()
    return render_template('plans.html', title='Plans', plans=config.list_plans(), client=config.client)


@app.route("/containeraction", methods=['POST'])
def containeraction():
    """
    start/stop/delete container
    """
    config = Kconfig()
    k = config.k
    if 'name' in request.form:
        name = request.form['name']
        action = request.form['action']
        if action == 'start':
            result = dockerutils.start_container(k, name)
        elif action == 'stop':
            result = dockerutils.stop_container(k, name)
        elif action == 'delete':
            result = dockerutils.delete_container(k, name)
        else:
            result = "Nothing to do"
        print(result)
        response = jsonify(result)
        response.status_code = 200
        return response
    else:
        failure = {'result': 'failure', 'reason': "Invalid Data"}
        response.status_code = 400
        return jsonify(failure)


@app.route('/templates')
def templates():
    """
    retrieves templates
    """
    config = Kconfig()
    k = config.k
    templates = k.volumes()
    return render_template('templates.html', title='Templates', templates=templates, client=config.client)


@app.route('/templatecreate')
def templatecreate():
    """
    create template
    """
    config = Kconfig()
    k = config.k
    pools = k.list_pools()
    return render_template('templatecreate.html', title='CreateTemplate', pools=pools, templates=sorted(TEMPLATES), client=config.client)


@app.route("/templateaction", methods=['POST'])
def templateaction():
    """
    create/delete template
    """
    config = Kconfig()
    if 'pool' in request.form:
        pool = request.form['pool']
        action = request.form['action']
        if action == 'create' and 'pool' in request.form and 'template' in request.form:
            pool = request.form['pool']
            template = request.form['template']
            url = request.form['url']
            cmd = request.form['cmd']
            if url == '':
                url = None
            if cmd == '':
                cmd = None
            result = config.handle_host(pool=pool, template=template, download=True, url=url, cmd=cmd)
        else:
            result = "Nothing to do"
        print(result)
        response = jsonify(result)
        print(response)
        response.status_code = 200
        return response
    else:
        failure = {'result': 'failure', 'reason': "Invalid Data"}
        response = jsonify(failure)
        response.status_code = 400
        return response


@app.route('/isos')
def isos():
    """
    retrieves isos
    """
    config = Kconfig()
    k = config.k
    isos = k.volumes(iso=True)
    return render_template('isos.html', title='Isos', isos=isos, client=config.client)


@app.route('/containerprofiles')
def containerprofiles():
    """
    retrieves container profiles
    """
    config = Kconfig()
    profiles = config.list_containerprofiles()
    return render_template('containerprofiles.html', title='ContainerProfiles', profiles=profiles, client=config.client)


def run():
    app.run(host='0.0.0.0', port=port, debug=debug)


if __name__ == '__main__':
    run()
