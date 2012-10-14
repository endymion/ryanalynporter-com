---
layout: post
title: "Authorizing Users Between Web Sites with Open Sesame"
description: Use a cryptographic hash to pass authenticated traffic between two web sites.
date: 2009-06-25
comments: true
categories: [Ruby, Rails, Sinatra]
---

_{{ page.description }}_

When I was building the Tiesto.com web site and Tiesto's fan club web site, InTheBooth.com, I needed a way to send authorized traffic from the members-only InTheBooth.com web site to ticket sale pages at Venue Driver (ticketdriver.com) to members-only pre-sale ticket-sale pages that the general public could not access.  But I needed the Tiesto.com web site to be completely independent from the VenueDriver.com web site.  I needed some way to authorize users on the VenueDriver.com web site from the InTheBooth.com web site, even though the two sites needed to run in different cloud environments, with different databases.

[Open Sesame](https://github.com/endymion/open-sesame) was the solution that I came up with.  It generates an authorization token by packaging a time stamp with a cryptographic hash of that time stamp plus a secret phrase.  The receiving end can take the time stamp and the secret that it also knows about, and generate a cryptographic hash of its own.  The it can compare that hash to the hash included in the token.  If the two are the same, then the token is verified.

I also needed a way to pass parameters from one site to another, and so I added an ```OpenSesame::Message``` class, for protecting the integrity of a string without encrypting it.

<!-- more -->

# Update - October 13, 2012

When I originally built OpenSesame, I needed it for passing traffic between two Rails apps.  Tiesto.com, and VenueDriver.com.  Recently, I wanted to use it to pass authorized traffic between two Sinatra apps.  I discovered that I had built it to depend on Rails.  And also to depend on both sites being on computers that are in the UTC time zone.  I rebuilt OpenSesame to use Ruby, without Rails.  I packaged it as a Ruby gem and published it on RubyGems.org.  I also added Yardoc documentation, and I confirmed 100% RSpec test coverage using SimpleCov.

# Mechanism

Web Site A has an authenticated user that it wants to send to a protected feature on Web Site B.  It generates an authorization token that consists of a cryptographic hash of a timestamp plus a secret, plus the timestamp in plaintext.

Example:

    timestamp: 2009-06-25T10:34:29-04:00
    secret: "OPEN SESAME"
    token: 20090625T1034-93a9d935fc64285645870a59db0d287b58f7caea

Web Site B then checks that the timestamp is not more than an hour old, and it checks to verify that the timestamp plus the shared secret produces the correct hash.  Web Site B should deny access with a 401 response if the authentication token does not verify.

# Installation

    cd your_app
    script/plugin install git://github.com/endymion/open-sesame.git

# Usage

The default secret is "OPEN SESAME".  You should change that because the default secret is public knowledge.  Add the secret to your config/environment.rb:

    OPEN_SESAME_SECRET = "Don't tell anybody, this is a secret!"

Or, if you want to keep that secret out of your source code then you can use an environment variable, like ```ENV['OPEN_SESAME_SECRET']```.  You can configure that environment variable on Heroku, for example, by giving this command to the terminal:

    heroku config:add OPEN_SESAME_SECRET="Don't tell anybody, this is a secret!"

For example, with Rails, you could do this in a controller in the first web app:

    token = OpenSesame::Token.generate(OPEN_SESAME_SECRET)
    redirect_to "http://second-app.net?token=#{token}"

In the second Rails app, you can verify the presence and validity of the token with:

    before_filter :check_token
    def check_token
      return if session[:open_sesame_verified]
      if params[:token].blank? || !OpenSesame::Token.verify(params[:token], OPEN_SESAME_SECRET)
        render :text => 'access denied', :status => 401
      end
      session[:open_sesame_verified] = true
    end

# Signing messages

You can also pass signed parameters.  Let's say you want to identify each user and you don't want them to mess with the ID that you pass.

    message: 123456789
    secret: "OPEN SESAME"
    token: 123456789-e349b9416e2b9f6954e80f03a5bb63d3f7401b70

From the first web app:

    token = OpenSesame::Token.generate(OPEN_SESAME_SECRET)
    username = OpenSesame::Message.generate('username', OPEN_SESAME_SECRET)
    redirect_to "http://second-app.net?token=#{token}&username=#{username}"

In the second app, you can verify both the token and any parameters:

    before_filter :check_token
    def check_token
      return if session[:open_sesame_verified]
      if params[:token].blank? || !OpenSesame::Token.verify(params[:token], OPEN_SESAME_SECRET)
        render :text => 'access denied', :status => 401
      end
      params.keys.each do |param|
        if OpenSesame::Mesage.verify(params[param])
          session[param] = OPenSesame::Message.message(params[param], OPEN_SESAME_SECRET)
        end
      end
      session[:open_sesame_verified] = true
    end

# The Ruby gem

The gem is hosted at [RubyGems](https://rubygems.org/gems/open-sesame), and the documentation is hosted at [RubyDoc.info](http://rubydoc.info/gems/open-sesame).  The code, of course, is hosted on [GitHub](https://github.com/endymion/open-sesame).