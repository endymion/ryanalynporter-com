---
title: Resizing thumbnails on demand with Paperclip and Rails
layout: post
description: How to generate Paperclip attachment thumbnails on demand instead of in advance.
date: 2012-06-07
comments: true
categories: [Ruby, Rails, Paperclip]
---

_{{ page.description }}_

If you have a Rails app that supports image uploads, then you probably use [Paperclip](https://github.com/thoughtbot/paperclip). Paperclip codifies an assumption about attachment handling: that you know in advance all of the thumbnail sizes that your web site will need for your image attachments, and that you want to generate those thumbnails when attachments are uploaded.

But what if you need to be able to display thumbnails at any size, specified by request parameters? What if you want to upload image attachments without generating thumbnails, so that you can dynamically
resize the images just-in-time (JIT) at any size specified by a user-editable view template?

### Resizing thumbnails just in time

Fortunately, Paperclip is flexible enough to handle that kind of scenario. This article demonstrates how to set up dynamic, just-in-time image resizing for Paperclip attachments in this [example Rails 3.2.5 app](https://github.com/endymion/paperclip-just-in-time-resizing).

<!-- more -->

First, we start with a basic [generated Rails 3.2.5 app](https://github.com/endymion/paperclip-just-in-time-resizing/commit/0a0b2babfbfdb6fc1ea4e1201b6fe334169a9b5a).  Then we add a [scaffold for an Image model](https://github.com/endymion/paperclip-just-in-time-resizing/commit/f408d1ccf83b70200e8f262fa95d6c7bef8e4cfc).  Then we [add a Paperclip attachment](https://github.com/endymion/paperclip-just-in-time-resizing/commit/358648128b63ecb4d17649c479b46130d5d336f1) called "attachment" to the Image model, with support for uploading an image and displaying the uploaded image.

### An Active Record model with a Paperclip attachment

You might have an Active Record model or two in your Rails app that supports Paperclip attachments
that looks something like the Image model at this point:

{% codeblock lang:ruby %}
class Image < ActiveRecord::Base
  has_attached_file :attachment,
    :storage => :s3,
    :bucket => ENV['S3_BUCKET_NAME'],
    :s3_credentials => {
      :access_key_id => ENV['AWS_ACCESS_KEY_ID'],
      :secret_access_key => ENV['AWS_SECRET_ACCESS_KEY']
    }
  attr_accessible :attachment
end
{% endcodeblock %}

### Works with S3 or local storage

We're using S3 for storage in the example, so if you want to run the example then you'll need to set up an S3 bucket for the example app and set some environment variables before you run the server:

    export AWS_ACCESS_KEY_ID='YOUR_ID'
    export AWS_SECRET_ACCESS_KEY='YOUR_KEY'
    export S3_BUCKET_NAME='paperclip-just-in-time-resizing'

### Use a Ruby Proc to add a style to the model instance

At this point, we can add a new Image to the app, and you can see the image on the "show" action. So how do
we set up dynamic thumbnails? We do that by [setting
up](https://github.com/endymion/paperclip-just-in-time-resizing/commit/131dfd2243623f5870e0d3aa6307f8573ece8b92#L0R11)
the ```:styles``` for the ```attachment``` to be a Ruby Proc, so that it's evaluated dynamically each time,
by adding:

{% codeblock lang:ruby %}
:styles => Proc.new { |attachment| attachment.instance.styles }
{% endcodeblock %}

That Proc references the ```styles``` method on the Image model:

{% codeblock lang:ruby %}
def styles
  unless @dynamic_style_format.blank?
    { dynamic_style_format_symbol => @dynamic_style_format }
  else
    {}
  end
end
{% endcodeblock %}

The ```Image#styles``` method normally returns an empty hash, which would mean that only the ```:original```
style would exist.  But if there is a ```@dynamic_style_format``` set for this instance of the Image
model, then it will dynamically add a style to the list, with a symbol name derived from URL encoding
the geometry format for the style.  So that, for example, the style "150x150>" would result in a style
with the configuration: ```{ :150x150%3E => '150x150>' }```.  The method that generates the symbol from
the geometry format string is very simple:

{% codeblock lang:ruby %}
def dynamic_style_format_symbol
  URI.escape(@dynamic_style_format).to_sym
end
{% endcodeblock %}

### Resize the attachment thumbnail on demand

Finally, the real work is handled by the ```Image#dynamic_attachment_url``` method, which sets the
current ```@dynamic_style_format``` for the Image instance so that the instance will include the
dynamic style.  Then it checks to see if a thumbnail already exists for the specified geometry.
It generates a thumbnail only if necessary, and then it returns a URL for that thumbnail.

{% codeblock lang:ruby %}
def dynamic_attachment_url(format)
  @dynamic_style_format = format
  attachment.reprocess!(dynamic_style_format_symbol) unless attachment.exists?(dynamic_style_format_symbol)
  attachment.url(dynamic_style_format_symbol)
end
{% endcodeblock %}

### Use any thumbnail geometry format in your view templates

This method allows you to specify a custom style format in a view template:

    <%= image_tag @image.attachment.url %>
    <%= image_tag @image.dynamic_attachment_url("150x150>") %>

The second ```image_tag```, above, uses the ```Image#dynamic_attachment_url``` method to dynamically
generate a thumbnail with a 150 x 150 bounding box.  Instead of specifying ```@image.attachment.url(:original)``` or ```@image.attachment.url(:thumbnail)``` or some other
pre-determined thumbnail style, you can specify any style format and the Image model will
generate the thumbnail just-in-time.

### The final Active Record model with dynamic thumbnails

Wrapping it all up, the Image model looks like this:

{% codeblock lang:ruby %}
require 'uri'

class Image < ActiveRecord::Base
  has_attached_file :attachment,
    :storage => :s3,
    :bucket => ENV['S3_BUCKET_NAME'],
    :s3_credentials => {
      :access_key_id => ENV['AWS_ACCESS_KEY_ID'],
      :secret_access_key => ENV['AWS_SECRET_ACCESS_KEY']
    },
    :styles => Proc.new { |attachment| attachment.instance.styles }
  attr_accessible :attachment
  
  def dynamic_style_format_symbol
    URI.escape(@dynamic_style_format).to_sym
  end
  
  def styles
    unless @dynamic_style_format.blank?
      { dynamic_style_format_symbol => @dynamic_style_format }
    else
      {}
    end
  end

  def dynamic_attachment_url(format)
    @dynamic_style_format = format
    attachment.reprocess!(dynamic_style_format_symbol) unless attachment.exists?(dynamic_style_format_symbol)
    attachment.url(dynamic_style_format_symbol)
  end
  
end
{% endcodeblock %}

### Providing a controller action for dynamic thumbnails

The ```Image#dynamic_attachment_url``` method enables you to specify any thumbnail size from inside
of one of your Rails app's view templates.  But what if the images will be embedded on other web
sites?  What if you need to be able to provide a URL for an image that includes thumbnail size
parameters?  That's really easy, given what we already have.

First, [add a route](https://github.com/endymion/paperclip-just-in-time-resizing/commit/4582fb06101a80831c1ae9db57265f430fb036d4) for the action that you want.  In config/routes.rb:

{% codeblock lang:ruby %}
resources :images do
  member do
    get 'thumbnail'
  end
end
{% endcodeblock %}

Then [add a simple controller action](https://github.com/endymion/paperclip-just-in-time-resizing/commit/08728756e1bcad4cd914b39beb39ab033b181cfc) that redirects to the URL returned by ```Image#dynamic_attachment_url```.

{% codeblock lang:ruby %}
def thumbnail
  @image = Image.find(params[:id])
  redirect_to @image.dynamic_attachment_url("#{params['width']}x#{params['height']}>")
end
{% endcodeblock %}

Now we can call something like ```http://localhost:3000/images/1/thumbnail?width=300&height=300```
to get an image thumbnail that is resized just in time.  The second time that you go to the same
URL, you will see a much faster response because the thumbnail will already be waiting on S3 and
you will be redirected to it immediately.