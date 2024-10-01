from flask import render_template, redirect, url_for, flash,request
from flask_login import login_user, logout_user, login_required, current_user
from app import app, db
import os
from app.forms import RegistrationForm, LoginForm, InstanceForm
from app.models import User, Plan, Instance
from .forms import CreateInstanceForm
import random
import subprocess

from proxmoxer import ProxmoxAPI

@app.route('/')
@app.route('/home')
def home():
    plans = Plan.query.all()
    return render_template('home.html', plans=plans)

@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Account created!', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.password == form.password.data:
            login_user(user)
            return redirect(url_for('home'))
        else:
            flash('Login Unsuccessful. Please check username and password', 'danger')
    return render_template('login.html', form=form)




@app.route('/create_instance', methods=['GET', 'POST'])
def create_instance():
    form = CreateInstanceForm()

    # Populate the plan choices
    form.plan_id.choices = [(plan.id, plan.name) for plan in Plan.query.all()]

    if form.validate_on_submit():
        plan_id = form.plan_id.data
        plan = Plan.query.get(plan_id)

        # Connect to Proxmox
        proxmox = ProxmoxAPI('your_proxmox_host', user='root@pam', password='your_password', verify_ssl=False)

        # Generate unique VM ID
        vmid = get_next_vmid()

        # Generate random IP and SSH port
        ip_address = generate_random_ip()
        ssh_port = generate_random_ssh_port()

        # Create the LXC instance
        hostname = f'container-{vmid}'

        proxmox.nodes('your_node_name').lxc.create(
            vmid=vmid,
            hostname=hostname,
            storage='local',
            template='your_template',
            cores=plan.cpus,
            memory=plan.ram,
            swap=0,
            net0=f'name=eth0,bridge=vmbr0,ip={ip_address},gw=10.10.10.1'
        )

        # Call the function to update the NAT scripts
        update_nat_scripts(vmid, ip_address, ssh_port)

        # Save the instance to the database
        instance = Instance(name=hostname, ip_address=ip_address, ssh_port=ssh_port, vmid=vmid, user_id=current_user.id)
        db.session.add(instance)
        db.session.commit()

        flash('Instance created successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('create_instance.html', form=form)





def get_next_vmid():
    used_vms = [instance.vmid for instance in Instance.query.all()]
    next_vmid = 100  # Start from 100 or any base ID you want

    while next_vmid in used_vms:
        next_vmid += 1

    return next_vmid


def generate_random_ip():
    # Generate a random IP from 10.10.10.3 to 10.10.10.254
    last_octet = random.randint(3, 254)
    return f'10.10.10.{last_octet}'

def generate_random_ssh_port():
    # Generate a random port between 1024 and 65535
    return random.randint(1024, 65535)

def run_nat_post_up_script():
    # Define the path to your nat-post-up.sh script
    nat_post_up_path = '/root/nat-post-up.sh'

    # Execute the script
    subprocess.run([nat_post_up_path], shell=True, check=True)

def update_nat_scripts(vmid, ip_address, ssh_port):
    # Define the paths to your NAT scripts
    nat_pre_down_path = '/root/nat-pre-down.sh'
    nat_post_up_path = '/root/nat-post-up.sh'

    # Update the nat-pre-down.sh script
    with open(nat_pre_down_path, 'a') as pre_down_script:
        pre_down_script.write(f"iptables -t nat -D PREROUTING -i vmbr0 -p tcp --dport {ssh_port} -j DNAT --to {ip_address}:22\n")

    # Update the nat-post-up.sh script
    with open(nat_post_up_path, 'a') as post_up_script:
        post_up_script.write(f"iptables -t nat -A PREROUTING -i vmbr0 -p tcp --dport {ssh_port} -j DNAT --to {ip_address}:22\n")



@app.route('/start_instance/<int:instance_id>', methods=['POST'])
@login_required
def start_instance(instance_id):
    instance = Instance.query.get_or_404(instance_id)
    
    # Connect to Proxmox
    proxmox = ProxmoxAPI('your_proxmox_host', user='root@pam', password='your_password', verify_ssl=False)

    # Start the LXC instance
    proxmox.nodes('your_node_name').lxc(instance.vmid).status.start.post()

    flash(f'Instance {instance.name} started!', 'success')
    return redirect(url_for('dashboard'))

@app.route('/stop_instance/<int:instance_id>', methods=['POST'])
@login_required
def stop_instance(instance_id):
    instance = Instance.query.get_or_404(instance_id)
    
    # Connect to Proxmox
    proxmox = ProxmoxAPI('your_proxmox_host', user='root@pam', password='your_password', verify_ssl=False)

    # Stop the LXC instance
    proxmox.nodes('your_node_name').lxc(instance.vmid).status.stop.post()

    flash(f'Instance {instance.name} stopped!', 'success')
    return redirect(url_for('dashboard'))



@app.route('/dashboard')
@login_required
def dashboard():
    instances = Instance.query.filter_by(user_id=current_user.id).all()  # Get all instances for the logged-in user
    return render_template('dashboard.html', instances=instances)





@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))
