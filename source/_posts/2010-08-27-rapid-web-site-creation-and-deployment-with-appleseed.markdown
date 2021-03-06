---
layout: post
title: "Rapid Web Site Creation And Deployment With Appleseed"
description: Create a Rails project, push it to GitHub, and deploy it to Heroku -- all with one command.
date: 2010-08-27
comments: true
categories: [Ruby, Rails, Heroku, GitHub]
---

{% img /images/posts/appleseed/appleseed.png %}

# Appleseed

Appleseed provides a generator for creating a new web site project with
Rails 3, adding things like HAML and Compass to the new project,
creating a Git repository for the new project, pushing that repository
to GitHub, and then deploying the site to Heroku. All with one command.

This utility is designed to assist graphic designers in rapidly creating
new web sites, for high-volume web shops. A graphic designer can create
a site, push the code to GitHub, and deploy the site to Heroku without
the assistance of a developer. Then a developer can easily join the
project to build out the back-end and assist the graphic designer with
the front-end.

<!-- more -->

Here is an [example GitHub project](http://github.com/endymion/generated-by-appleseed) that Appleseed generated, and here is the [Heroku web application](http://generated-by-appleseed.heroku.com/) for that example project. Note the example layout, default home page, and Blueprint styling provided by Compass.

# Usage

## Step 1: Install Appleseed

Open a Terminal window and copy the following command into the window:

    gem install appleseed

## Step 2: Generate Web Application Project

In that same terminal, go to your local projects folder:

    cd \~/projects

Then generate a new project by giving Appleseed the name of your new
project:

    appleseed my-new-rails-app

Appleseed will create the following:

* A Rails 3 web application project in ```\~/projects/my-new-rails-app```
* A GitHub repository at ```git@github.com:[you]/my-new-rails-app.git```
* A Heroku app at ```http://my-new-rails-app.heroku.com```

== Step 3: Run The Web Site

Your new web application is already running on Heroku. But for you to
make changes, you'll have to be able to run the web site on your local
computer. You might want to open a new tab in your Terminal window for
the server. Then change to the new project folder in your Terminal
window:

    cd \~/projects/my-new-rails-app

Then run the Rails server with:

    rails server

Then go to ```http://localhost:3000``` in a web browser, and you should see
your new web site.

# Step 4: Make Changes

After you make changes to your web site project, use these Terminal
commands to push the changes to GitHub and Heroku:

    git add .
    git commit -m "Update."
    git push github master git push heroku master

If the "git push" operation produces an error, then it probably means
that somebody else has made a change to the same web site and you need
to merge your update with their update before you can push your update.
Do this:

    git pull github master

Then after Git pulls the other person's update and merges it with your
update, proceed with the ```git push github master```, above.

If Git reports that there has been a conflict, then commit the conflict
and push it to GitHub, but do NOT push to Heroku:

    git add .
    git commit -m "Conflict."
    git push github master

# Step 5: Deploy Your Changes

Deploying your web site after you make changes is really easy. Just push
to the "heroku" remote:

    git push heroku master

# Step 6: Goto Step 4

Repeat until the money runs out.

# Final Product

Appleseed generates a web application that's more than just the default
generated Rails 3 template. Instead of just a default working Rails
application, you also get a default ("root") controller and a root route
to a home page. You get a layout based on HAML, and the Blueprint CSS
framework provided by Compass. You get the RSpec and Cucumber testing
frameworks and sample tests. The final product is ready for new HTML/CSS
files and images from graphic designers.

The final product does NOT contain any database models, or an
administrative back-end. It only includes a default controller so that
graphic designers can easily add HTML files.

# Options

## --no-github

You can use the ```--no-github``` option to tell Appleseed NOT to create a new
project at GitHub.

## --no-heroku

You can use the ```--no-heroku``` option to tell Appleseed NOT to deploy your new web application to Heroku.

## --template

By default, [the default template](http://github.com/endymion/appleseed/raw/master/templates/default.rb)
will be applied to the new project. You can tell Appleseed to use your
own custom template with the ```--template``` option. For example:

    appleseed --template \~/templates/my-template.txt new-web-application

A simple way to customize the Rails template that Appleseed uses is to
fork the Appleseed project on GitHub and then edit the
```lib/appleseed/generator.rb``` file to use your forked project's default
template URL instead of ```http://github.com/endymion/appleseed/raw/master/templates/default.rb```.

# Prerequisites

## Tools

* Git
* Ruby

# Ruby Gems

* Rails ("gem install rails")
* Heroku ("gem install heroku")

# GitHub Account

You will need an account at [GitHu](http://www.github.com). [Set
up](http://help.github.com/git-email-settings/) your GitHub name and
email on your local computer. Then also [set
up](http://github.com/blog/180-local-github-config) your GitHub user and
API token on your local computer. Then make sure that you have an [SSH
key](http://help.github.com/mac-key-setup/) set up and added to your
GitHub account.

## Heroku Account

You will also need an account at
[Heroku](http://docs.heroku.com/heroku-command). Install the Heroku gem
and then use "heroku keys:add" to link your local computer to your
Heroku account.

## Appleseed

Once you have the above prerequisites, install Appleseed with ```gem
install appleseed```. Now you're ready to generate web sites!

# Inspiration

* [Jeweler](http://github.com/technicalpickles/jeweler)
* [Johnny Appleseed](http://en.wikipedia.org/wiki/Johnny\_Appleseed)

# Copyright

Copyright (c) 2010 Ryan Alyn Porter. See LICENSE for details.

Appleseed logo by Jessie Angles.