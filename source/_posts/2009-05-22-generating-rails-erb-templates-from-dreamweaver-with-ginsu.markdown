---
layout: post
title: "Generating Rails ERB Templates From Dreamweaver With Ginsu"
description: Bring graphic designers into your agile process by generating Rails templates automatially.
date: 2009-05-22
comments: true
categories: [Ruby, Rails, ERB, Dreamweaver, hpricot]
---

_{{ page.description }}_

Rails applications are not always born as Rails applications. Sometimes
graphic designers create web designs using tools like Dreamweaver and
then pass them off to software developers for implementation as web
applications

But Rails has a different model for a web site than a graphic designer's authoring tool like BBEdit. Rails thinks in terms of routes that lead to actions that render using templates that can use layouts, but web authoring tools like Dreamweaver and Rapidweaver think in terms of pages. Every page includes the whole layout.

Ginsu plugs your graphic designers into the agile software development process, by automating the creation of ERB templates and Rails layout files from HTML files. Ginsu can create hybrid web sites with some sections served as static content and some sections powered by dynamic Rails actions, or you can convert every page into an action, and every Dreamweaver layout into a Rails layout.  It's not specific to Dreamweaver because it slices out content based on HTML CSS selectors, so you can use it with any HTML authoring tool.

<!-- more -->

The Problem
-----------

You work in a high-volume web shop. Your job is the nerd stuff:
programming the dynamic parts of web projects and dealing with site
implementation and hosting. A producer gives you a .zip file and tells
you that the deadline to get the site hosted is that afternoon. The .zip
file contains static .html, .css, image and Flash files from a
Dreamweaver project that a graphic designer developed. Then, the
punchline: “Only pages X and Y need to be dynamic, leave the rest
static. We’re still designing it. Oh and we’ll be updating this part of
page X and this part of page Y once a week.”

You don’t want to work with a graphic designer every week to update your
.erb or .haml files because that makes updates very expensive, which is
not very agile. You don’t want to configure your web server to serve
only a few routes from your Rails app because making changes is hard and
so that’s also not very agile. You can’t implement a CMS back-end for
making it all irrelevant because you work in a high-volume shop and you
only have an hour.

You need a way to bring your graphic designer into the agile process, so
that you and the designer can both make updates to your respective areas
of the project.

The Solution
------------

    cd yourapp
    mkdir static

Copy your static web site from your graphic designer into your Rails
application’s new ```static``` directory. If your static web site has a root index file called ```index.html```, then your Rails app should have a file called ```static/index.html```.

Configure Ginsu to slice sections of pages from the static web site into
partial templates in your Rails application by adding slicing
instructions to your ```config/initializers/ginsu.rb```:

    # Create a 'header' partial by plucking header HTML from static/index.html using a CSS selector.
    ginsu.partials << { :css => 'h3.r a.l', :static => 'index.html', :partial => 'header' }

    # Create a 'header' partial by plucking header HTML from static/index.html using an xpath selector.
    ginsu.partials << { partial :xpath => '//h3/a[@class="l"]', :static => 'index.html', :partial => 'header' }

    # Just use the 'search' parameter to use either CSS or xpath.
    ginsu.partials << { :search => 'h3.r a.l', :static => 'index.html', :partial => 'header' }
    ginsu.partials << { :search => '//h3/a[@class="m"]', :static => 'index.html', :partial => 'header' }

    # Create symbolic links in the public/ directory of the Rails app for selected sections and files.
    ginsu.links << { :static => 'galleries' }
    ginsu.links << { :static => 'events' }
    ginsu.links << { :static => 'holdout.html' }

    Now when you run:

    rake ginsu:slice

…Ginsu will find the header in your ```static/index.html``` file and create a partial in ```app/views/\_header.html.erb``` with the contents of the HTML element that it locates using your CSS or xpath selector.

Using this technique does not require your graphic designer to make any
changes to the Dreamweaver project. You don’t have to tag the section
that you want to slice out, you simply describe where it’s located and
Ginsu will find it and slice it out. You bring your graphic designers
into the agile process by enabling them to update parts of the web site
with their tools, without learning Rails.

Installation
------------

Install the Ginsu gem in your Rails application with:

    script/plugin install git://github.com/endymion/ginsu.git

Generate your initializer, for configuring Ginsu:

    script/generate ginsu

Configure
---------

The Ginsu configuration is in the initializer file ```config/initializers/ginsu.rb```:

    require 'ginsu'
    Ginsu::Knife.configure do |ginsu|

      # The default location of the static web site is 'site', but maybe your static
      # site includes 150 MB worth of Photoshop .psd files and you don't want those
      # in your Capistrano deployments.  Change the source path here if you want.
      ginsu.source = '/home/webproject/site'

      ginsu.partials << { :search => '#header', :static => 'index.html', :partial => 'header' }
      ginsu.partials << { :search => '#footer', :static => 'index.html', :partial => 'footer' }

      ginsu.links << { :static => 'galleries' }
      ginsu.links << { :static => 'news' }

    end

Features
--------

### partial

A partial is the content of an HTML element that Ginsu will partial out
of a static HTML document and drop into a Rails partial template.

### link

A link is a page or a folder that you want to be entirely served as
static content. Ginsu will create symbolic links in your Rails
application’s ```public/``` directory for each link.
