---
title: Simple Redis caching in Ruby
layout: post
description: A utility method for caching the result of any block of Ruby code.
date: 2012-06-12
comments: true
categories: [Ruby, Redis]
---

_{{ page.description }}_

[Redis](http://redis.io/) is a simple and very fast key-value store, that can be used for all kinds of things. [Resque](https://github.com/defunkt/resque), for example, is a system built on Redis for
processing background jobs or even [scheduled jobs](https://github.com/bvandenbos/resque-scheduler). Redis can be used for all kinds of different things, and so it has a very generalized API that doesn't
make any assumptions about how you're going to use it. The Redis API includes simple methods like ```get``` and ```set``` and ```expire```. And the [Ruby gem for Redis](https://github.com/redis/redis-rb)
is a thin layer over the standard Redis API.

### Caching expensive operations with Redis

But when most people use Redis, they tend to use it for caching values in a web application, like you would use [memcached](http://memcached.org/). And if you use Redis for caching, then you might find yourself writing the same sort of code structure over and over:

{% codeblock lang:ruby %}
if (something = redis.get(redis_key = "the cache key")).nil?
  redis.set(
    redis_key,
    (something =
      # Some really slow calculation or data access happens here.
    )
  )
  redis.expire redis_key, 300 # seconds = 5 minutes.
end

# Use the "something" value that was calculated (or cached) above.
use(something)
{% endcodeblock %}

It's great that ```Redis#get``` and ```Redis#set``` and ```Redis#expire``` are all so simple. But if you're going to wrap expensive operations in Redis caching frequently, then what you really need is a ```Redis#cache``` method.

<!-- more -->

### Monkey patching to the rescue

With Ruby, you can monkey patch anything, so it's not difficult to add a new convenience method to
the Ruby bindings for Redis.  We can just open the Redis class and drop in a new method.  You can simply add a file called ```lib/redis_cache.rb``` to a Ruby project in order to add a ```cache``` method ot the Redis API:

{% codeblock lib/redis_cache.rb lang:ruby %}
class Redis
  
  def cache(key, expire=nil)
    if (value = get(key)).nil?
      value = yield(self)
      set(key, value)
      expire(key, expire) if expire
      value
    else
      value
    end
  end
  
end
{% endcodeblock %}

The new ```Redis#cache``` method accepts three things: a ```key``` argument, an optional ```expire```
argument, and a block of code. First, it checks Redis for a value at the given key. If one exists, then
it returns that value immediately. If one doesn't exist, then it uses the code block to generate a value.
Then it sets the Redis key to that value. Then it sets the expiration, in seconds, on that key, if there
was an expiration argument provided.

This simple code teaches Redis to speak the language of caching, simplifying your high-level
application code. Instead of the code pattern shown in the first code sample, distracting the reader
from the problem at hand with caching details, the application code can be all about the values that it
wants to calculate, with caching wrapped unobtrusively around the meat of the solution code.

For example, from the simple unit tests for the ```Redis#cache``` method:

{% codeblock test/unit/redis_cache_test.rb lang:ruby %}
require File.dirname(__FILE__) + '/../test_helper'
require 'redis'
require 'redis_cache'

class RedisCacheTest < Test::Unit::TestCase

  def test_cache_block_in_redis
    redis = Redis.new
    assert 42, redis.cache('key') { 42 }
    assert 42, redis.cache('key') { assert false,
      'This should never be executed' }
  end

  def test_cache_method_passes_redis_argument_to_block
    redis = Redis.new
    assert Redis, redis.cache('key') {|redis| redis.class }
  end

end
{% endcodeblock %}

If you have a ```do_something``` method that takes a long time to complete, then you can cache that
method at the key "key" with ```redis.cache('key') { do_something }```.  Simple.

### Recalculate every time

You might want to disable caching in development and test modes.  You can add support for disabling
caching by adding a second optional argument to the ```Redis#cache``` method:

{% codeblock lib/redis_cache.rb lang:ruby %}
class Redis
  
  def cache(key, expire=nil, recalculate=false)
    if (value = get(key)).nil? || recalculate
      value = yield(self)
      set(key, value)
      expire(key, expire) if expire
      value
    else
      value
    end
  end
  
end
{% endcodeblock %}

If ```recalculate``` is true, then the code block will be executed every time.  So you can make
that value true in development and test modes like this:

{% codeblock lang:ruby %}
value = redis.cache('key', 60,
  ['test', 'development'].include? Rails.env) do  
  "This will always happen."
end
{% endcodeblock %}

### Add timeout and default parameters

Generally when you use this kind of caching, you're using it to cache the results of some operation that's really slow.  If that operation is really slow because it involves the network, then maybe sometimes it might time out, and you might want to specify a default value to use instead when it times out.  It's easy to add support for a timeout using Ruby's [Timeout class](http://www.ruby-doc.org/stdlib-1.9.3/libdoc/timeout/rdoc/Timeout.html), which is supported all the way back to Ruby 1.8.6.

At this point, it's definitely time to switch to named parameters, so that the code that calls this method will be more clear and readable.

{% codeblock lib/redis_cache.rb lang:ruby %}
class Redis
  
  def cache(params)
    key = params[:key] || raise(":key parameter is required!")
    expire = params[:expire] || nil
    recalculate = params[:recalculate] || nil
    expire = params[:expire] || nil
    timeout = params[:timeout] || 0
    default = params[:default] || nil

    if (value = get(key)).nil? || recalculate

      begin
        value = Timeout::timeout(timeout) { yield(self) }
      rescue Timeout::Error
        value = default
      end

      set(key, value)
      expire(key, expire) if expire
      value
    else
      value
    end
  end
  
end
{% endcodeblock %}

### Example usage

Here's an example of using the new ```Redis#cache``` method in a Rails app to cache the results of a call to the Twitter API, with a five-sectond timeout.  This example will return a default value of ```nil``` if the Twitter API times out.  But you could also pass a ```:default => { 'something?' }``` parameter in other scenarios.

{% codeblock lang:ruby %}
require 'redis'
require 'twitter'
require 'json'

redis = Redis.new

twitter_user = 'ryanalynporter'

tweet = redis.cache(
    :key => "twitter-user-timeline-#{twitter_user}",
    :expire => 300, # seconds, 5 minutes
    :timeout => 5,  # seconds
    # Recalculate every time when this is true.
    :recalculate => ['test', 'development'].include?(Rails.env)
  ) do
    Twitter.user_timeline(twitter_user, :count => 1).first.to_json
  end

unless tweet.nil?
  tweet = JSON.parse(tweet)
{% endcodeblock %}
