package "build-essential"

package "g++"

package "libpq-dev"

package "libxslt-dev"

package "libxml2-dev"

package "python-dev"

package "s3cmd"

# execute "rubygems" do
#   user "root"
#   command "gem update --system 2.4.1"
# end

gem_package "bundler" do
  action :install
  version '1.3.5'
end

execute "Run Bundler Install" do
  user "root"
  cwd "/vagrant"
  command "bundle install"
end