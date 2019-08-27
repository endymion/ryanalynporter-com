---
layout: post
title: "Need an FTP server?  Here's how to get there with Vagrant, EC2 and vsftp"
description: An example of using Vagrant's vagrant-aws plugin to launch an FTP server on EC2 using vsftp.
date: 2014-08-24 16:20
comments: true
categories: [EC2, Vagrant]
---

_{{ page.description }}_

When I was building Vault, the data warehouse for the [Hakkasan Group](http://www.hakkasangroup.com), I had to accommodate data sources that post data files to an FTP server.  I didn't want to compromise the security of the data warehouse by running an FTP daemon on an existing server in Vault's secure production environment, so I spun up a dedicated FTP server outside of that environment in the same
[Amazon EC2](http://aws.amazon.com/ec2/) data center.

No self-respecting [DevOps](http://en.wikipedia.org/wiki/DevOps) practitioner would set up
a server like that manually.  I used [Chef](http://www.getchef.com/chef/) to configure the
cloud instance.  But I also wanted to automate creating the instance, not just configuring it.
One way to do that is with the [Knife](http://docs.getchef.com/knife.html) tool in the Chef
suite of tools.  Knife is powerful, but using it is not simple, especially without a Chef server.
I wanted to automate as much of the process as possible, so that ideally creating the server
in the cloud is as simple as pressing a button and then sitting back and watching it happen.

To accomplish that, I turned to [Vagrant](https://www.vagrantup.com/), a tool originally
intended for creating development environments.  Now it's capable of a lot more. Vagrant's multi-
provider technology makes it easy to use the [vagrant-aws](https://github.com/mitchellh/vagrant-aws)
plugin to create cloud instances on Amazon EC2, or [vagrant-rackspace](https://github.com/mitchellh
/vagrant-rackspace) to use Rackspace, or [vagrant-google](https://github.com/mitchellh/vagrant-
google) for the Google cloud, or others, in addition to local development environments.

<!-- more -->

## Technology

My original plan was to use the [FTP support from Box.com](https://support.box.com/hc/en-us/articles/200520128-Using-Box-with-FTP), but the first data source was OpenTable.  Let's just say
that the technical people at OpenTable are apparently focused on things other than assisting
enterprise-level restaurant accounts with accessing their own data.  After over two months of
watching them fumble helplessly at getting their system to post files to Box.com, I gave up and told
them that I would set up the most vanilla FTP server imaginable.  (They still could barely figure it
out.)  If all that you need is a cloud FTP service, you might want to just go and get a
[Box.com](https://www.box.com/) account.  They're awesome.  I had to find a different way.

My goal was to get [vsftp](http://vsftpd.beasts.org/) running in the cloud with the most boring
and conventional configuration possible.  I used the [vagrant-aws](https://github.com/mitchellh/vagrant-aws) plugin
to create an [Ubuntu 12.04](http://releases.ubuntu.com/12.04/) cloud instance at
Amazon EC2.  I used the [vagrant-omnibus](https://github.com/schisamo/vagrant-omnibus) plugin to install [Chef](http://www.getchef.com/chef/),
and then I used Chef to provision the instance with vsftp, to configure it, and to
create the FTP user(s).  The whole thing is fully automated from the ```vagrant up```
command.

I used the new bursting
[T2.micro](http://aws.amazon.com/about-aws/whats-new/2014/07/01/introducing-t2-the-new-low-cost-general-purpose-instance-type-for-amazon-ec2/)
instance type that only costs $9.50 per month.  Plenty of power for an FTP site that only
handles a few transfers per day.

## Prerequisites

* Install [Git](http://git-scm.com/)
* Install [VirtualBox](https://www.virtualbox.org)
* Install [Vagrant](http://downloads.vagrantup.com/)
* Install the Vagrant-Omnibus plugin for Vagrant: ```vagrant plugin install vagrant-omnibus```

## Code

One of the goals of DevOps is to create servers with code like [this](https://github.com/endymion/ec
2-ftp/blob/master/cookbooks/development/configure/recipes/default.rb), instead of with manual labor
like [this](https://gist.github.com/aronwoost/1105007).  So you'll need to get some code.  The code
for creating this FTP server is stored in the
[endymion/ec2-ftp](https://github.com/endymion/ec2-ftp) project on GitHub.

Clone the project to your development system by opening a terminal and switching to the
folder on your machine where you want the code (suggestion: ```cd ~/projects```) and enter
this command: ```git clone git@github.com:endymion/ec2-ftp.git```.  If you can
```cd ec2-ftp``` then it worked.

The meat of the project is in the [Vagrantfile](https://github.com/endymion/ec2-ftp/blob/master/Vagrantfile) and in the [Chef recipe](https://github.com/endymion/ec2-ftp/blob/master/cookbooks/development/configure/recipes/default.rb).  When you give Vagrant
the ```vagrant up --provider=aws``` command, it looks in the Vagrantfile for the
[aws configuration section](https://github.com/endymion/ec2-ftp/blob/master/Vagrantfile#L5).
That section includes the [AMI](https://github.com/endymion/ec2-ftp/blob/master/Vagrantfile#L6)
to use, the [region](https://github.com/endymion/ec2-ftp/blob/master/Vagrantfile#L14) where you
want your cloud instance to run, and the [instance type](https://github.com/endymion/ec2-ftp/blob/master/Vagrantfile#L15).  The key and secret for accessing AWS comes from
[environment variables](https://github.com/endymion/ec2-ftp/blob/master/Vagrantfile#L7-L8)
that you need to set before you run ```vagrant up```, as well as the name of the 
[EC2 key pair](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/ec2-key-pairs.html) that
the vagrant-aws plugin will install on your new cloud instance, so that you can connect to it
with ```vagrant ssh```.

## Authentication

To spin up an EC2 machine you'll need a key and secret for accessing your AWS account.
Create an IAM user in a group with full access to EC2, and provide the key and secret
by setting two environment variables:

    export AWS_KEY=“[YOUR KEY]"
    export AWS_SECRET="[YOUR SECRET]”

To access the EC2 machine you'll need an EC2 key pair.  If you have a key pair in a file
called ```ec2-ftp.pem``` in the root of this project, then you can configure that
by setting two environment variables, like this:

    export AWS_KEYPAIR_NAME="ec2-ftp”
    export AWS_KEYPAIR_PATH="ec2-ftp.pem"

## Users

I needed to create a few FTP users, so that each different data source has its own login to the
server.  It's not good practice to store sensitive information like usernames and passwords
in any code repository, so I used a separate YAML configuration file that is not stored in the
Git repository.

You'll need to provide a ```users.yml``` file in the root of this project that contains a list of
users to set up on the server.  You can change this file after the server is running and then re-
provision later with Chef, using ```vagrant provision``` to make changes to the user list.

The format of the file is:

    username:
      password: 'password'
      shadow_hash: 'shadow_hash'

For example, if there are two users, ```foo``` and ```bar```, with the passwords ```password1```
and ```password2``` respectively, then the file should look like this:

    foo:
      password: 'password1'
      shadow_hash: '$1$yoursalt$u/huh9HuopXpub4Ha3SWO/'
    bar:
      password: 'password2'
      shadow_hash: '$1$yoursalt$AWgHV/EkLFgEsWORPVSjh.'

The ```password:``` entries are really just there for your benefit.  If you're storing them
somewhere more secure then they're not necessary.

Generate the shadow hashes with:

    openssl passwd -1 -salt "yoursaltphrase"

Use any salt phrase you like.

## Create the server

Once you have the prerequisite software, the code for setting up the server, your AWS
authentication, and your user list set up, you can create and configure the server with one
simple command:

    vagrant up --provider=aws

Now just sit back and watch it go.  Map a CNAME DNS entry to the instance once it's running,
and you're done.  If you need to add more users, then add new entries to your users.yml file
and then run Chef on the cloud instance again with:

    vagrant provision

## Security group

Make sure that you have ports 21 and 22 open in the security group for your instance.  Port 21
is for FTP, and port 22 is for SSH and SFTP.

## Connect to the server

Once the server is up, you can connect to it via SSH with Vagrant with the command:

    vagrant ssh

That's one of the reasons that Vagrant is awesome.  You don't need to keep track of the IP or
hostname of your instance, and you don't need to manually tell it what key pair file to use
when you connect.  Just tell Vagrant to give you an SSH connection and it will take you there.

You should also now be able to connect to your new FTP server from any FTP client, either with
straight FTP or with SFTP.  The Chef recipes create and install a
[self-signed certificate](https://github.com/endymion/ec2-ftp/blob/master/cookbooks/development/configure/recipes/default.rb#L7-L11) for sshd so that you don't have to.

## Read-only root folders

For security reasons, vsftp does not allow a user's home folder to be writable.  You could
override that to make things simple, but it's set up like that for a reason.  The best practice
is for a superuser to create a subfolder in each user's home folder and then use that for FTP
files.  I needed a custom setup in each user's home folder, but you could easily create a "files"
folder automatically in the Chef recipes if you want to automate that process for every user.