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

  # appX instance salt ninion
  # config.vm.define :web0-staging do |web0|
  #   web0.vm.network :private_network, ip: "10.10.10.3"
  #   web0.vm.hostname = "web0"

  #   web0.vm.synced_folder "conf/vagrant/keys/", "/etc/salt/keys"
  #   web0.vm.network :forwarded_port, guest: 22, host: 2221, auto_correct: true

  #   web0.vm.provider "virtualbox" do |v|
  #     v.name = "web0"
  #     v.customize ["modifyvm", :id, "--memory", "512"]
  #   end

  #   web0.vm.provision :salt do |config|
  #     config.minion_config = "conf/vagrant/minion.yaml"
  #     config.minion_key = "conf/vagrant/keys/minion.pem"
  #     config.minion_pub = "conf/vagrant/keys/minion.pub"
  #     config.verbose = true
  #     config.bootstrap_options = "-D"
  #     config.temp_config_dir = "/tmp"
  #   end
  # end
end
