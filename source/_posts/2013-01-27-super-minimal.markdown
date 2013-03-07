---
layout: post
title: "Super-minimal, pure-Javascript ad banner rotator"
description: A simple system for displaying weighted random ad banners, for when you don't really care about impression or click tracking.
date: 2013-01-27 14:43
comments: true
categories: [javascript, jquery]
---

_{{ page.description }}_

<iframe width="640" height="79" style="overflow: hidden;"
  src="/super-minimal-ads/banner.html?type=leaderboard"></iframe>

I still maintain a web forum that I set up over five years ago for the [Miami nightlife community](http://forum.talknightlife.com), but I can't afford to spend a lot of time dealing with it.  Recently, the PHP-based ad management package that I used (and never had time to update) was used as an attack vector, and so it had to be removed.  I needed a replacement but I just didn't have the time to deal with setting up a new ad package, and I don't really want to deal with any PHP software packages other than the forum software itself, phpBB 3.  I don't want the liability of needing to stay current with security updates for yet another piece of mission-critical software.

Then I realized: I don't care about tracking the impressions or clicks.  The site is fairly popular in its niche, and sometimes the ad space is worth money.  But in nightlife, generally advertisers only care about the length of the ad campaign (a week or two) and nothing else.  Nightlife advertisers are generally not sophisticated enough to even care about clicks or impression counts or ROI.

So why not just do it all in Javascript?  All of the work could be done by the client's browser, and there would be no possibility of a security breach through an outdated ad management system.  And it would work with PHP or Rails or even a static HTML site.  And so the [Super Minimal Ads](https://github.com/endymion/super-minimal-ads) project was born.  About an hour later, I was done.

<!-- more -->

### Banner setup files

The forum has two different types of banners, one for the main leaderboard and one for the flanks on the sides, so the ```type``` parameter makes it easy to use the same ```banner.html``` file for both ad zones.

Each banner includes a weight, and a URL.  It's generally not a good idea for humans to be editing raw JSON data, so I made that file a .js file, which makes it a little simpler to display a parse error message when there are problems.  Here's an example:

{% codeblock leaderboard.js lang:javascript %}
var banners = [
  {
    "img": "tnl-banner-steve-jobs-01.png",
    "url": "http://news.stanford.edu/news/2005/june15/jobs-061505.html",
    "weight": 1
  },
  {
    "img": "tnl-banner-steve-jobs-02.png",
    "url": "http://news.stanford.edu/news/2005/june15/jobs-061505.html",
    "weight": 1
  },
  {
    "img": "tnl-banner-steve-jobs-03.png",
    "url": "http://news.stanford.edu/news/2005/june15/jobs-061505.html",
    "weight": 1
  },
  {
    "img": "tnl-banner-steve-jobs-04.png",
    "url": "http://news.stanford.edu/news/2005/june15/jobs-061505.html",
    "weight": 1
  },
  {
    "img": "tnl-banner-steve-jobs-05.png",
    "url": "http://news.stanford.edu/news/2005/june15/jobs-061505.html",
    "weight": 4
  }
];
{% endcodeblock %}

The last ad in the list has a weight of four, so it will appear four times as often as any of the others.  So half of the time, the last banner will be displayed.

### Serving ad banners with Javascript

The file ```banner.html``` does all of the work.  It's a bare-bones HTML5 page, with no content.  It writes its own content with Javascript.  It looks in the query string for a ```type``` parameter, and uses that parameter to fetch a banner setup file.  The ```banners``` array from the setup file gets added to the namespace, and then the ```randomBanner()``` function picks a random banner based on the weights specified in the setup file.

{% codeblock banner.html lang:javascript %}
<!doctype html>
<meta charset=utf-8>
<title>ad banners</title>
<style>
body { margin: 0; }
</style>
<script src="//ajax.googleapis.com/ajax/libs/jquery/1.8.3/jquery.min.js"></script>
<script>

// Fetch the banner setup file.
var filename = getURLParameter("type")+".js";
jQuery.getScript(filename, function(){
  var banner = randomBanner();
  // Add the banner to the page body.
  $('body').append("<a target=\"tnl_ad\" href=\""+banner["url"]+"\">" +
    "<img src=\"banners/"+banner["img"]+"\"></a>");
})
  .fail(function(jqxhr, settings, exception) {
    console.log("Error parsing " + filename + ": " + exception.message);
  }
)

function randomBanner() {
    var totalWeight = 0, cummulativeWeight = 0, i;
    // Add up the weights.
    for (i = 0; i < banners.length; i++) {
        totalWeight += banners[i]["weight"];
    }
    console.log("Total weight: " + totalWeight);
    var random = Math.floor(Math.random() * totalWeight);
    // Find which bucket the random value is in.
    for (i = 0; i < banners.length; i++) {
        cummulativeWeight += banners[i]["weight"];
        if (random < cummulativeWeight) {
            return(banners[i]);
        }
    }
}

function getURLParameter(name){
  return decodeURI((RegExp(name + '=' + '(.+?)(&|$)').exec(location.search)||[,null])[1]);
}
</script>
{% endcodeblock %}

### Include it in the web site in an iframe

The last step is simply to include the ```banner.html``` file with a ```type``` parameter, in an iframe.  This is the code used to insert the banner at the top of this page:

{% codeblock site.html lang:javascript %}
<iframe width="640" height="79" style="overflow: hidden;" src="/super-minimal-ads/banner.html?type=leaderboard"></iframe>
{% endcodeblock %}

Don't like iframes?  Yeah, I don't either.  No problem, just add the script code directly to your site's page, and change the target in the ```$('body').append...``` to put the banner where you want it in your page.

### Requires no server-side code

The whole point of this system is to eliminate 100% of the server-side code for serving ads.  That eliminates any possible security risks associated with an ad management system.  And it also means that you can use it with PHP or Rails or .Net or Dart or any web framework of any kind.  Including no web framework, like this Octopress web site, which is hosted on Amazon S3, and doesn't use any server-side web framework at all.