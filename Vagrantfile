Vagrant.configure("2") do |config|
  config.vm.box = "precise32"
  config.vm.box_url = "http://files.vagrantup.com/precise32.box"
  config.ssh.forward_agent = true

  #### salt master ####
  config.vm.define :salt do |salt|
    salt.vm.network :private_network, ip: "10.10.10.2"
    salt.vm.hostname = 'salt'

    salt.vm.synced_folder "conf/roots/", "/srv/"
    salt.vm.network :forwarded_port, guest: 22, host: 2220, auto_correct: true

    salt.vm.provider "virtualbox" do |v|
      v.name = "salt"
      v.customize ["modifyvm", :id, "--memory", "1024"]
    end
  end

  #### web ####
  config.vm.define :web_staging do |web_staging|
    web_staging.vm.network :private_network, ip: "10.10.10.3"
    web_staging.vm.network :forwarded_port, guest: 80, host: 8090
    web_staging.vm.network :forwarded_port, guest: 443, host: 8089
    web_staging.vm.provider "virtualbox" do |v|
      v.name = "web-staging-vagrant"
      v.customize ["modifyvm", :id, "--memory", "1024"]
    end
  end

  #### database ####
  config.vm.define :db_staging do |db_staging|
    db_staging.vm.network :private_network, ip: "10.10.10.4"
    db_staging.vm.provider "virtualbox" do |v|
      v.name = "db-staging-vagrant"
      v.customize ["modifyvm", :id, "--memory", "1024"]
    end
  end
end
