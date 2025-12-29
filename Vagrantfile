Vagrant.configure("2") do |config|
  
  # We only need ONE VM. It will host all containers.
  config.vm.define "docker-vm" do |docker|
    docker.vm.box = "ubuntu/focal64" # Ubuntu 20.04
    docker.vm.hostname = "docker-host"
    
    # We give it a private IP so we can access it easily
    docker.vm.network "private_network", ip: "192.168.56.20"
    
    # CRITICAL: Forward the Gateway port
    # Your Laptop :3000 -> VM :3000 -> Container :3000
    docker.vm.network "forwarded_port", guest: 3000, host: 3000
    
    # Sync the project folder
    docker.vm.synced_folder ".", "/app"

    # Docker needs RAM! Give it at least 2GB since it runs 6 containers + Postgres
    docker.vm.provider "virtualbox" do |vb|
      vb.memory = "2048"
      vb.cpus = 2
    end
    
    # PROVISIONING: Install Docker automatically when VM starts
    docker.vm.provision "shell", inline: <<-SHELL
      # Uninstall old versions
      apt-get remove -y docker docker-engine docker.io containerd runc
      
      # Install prerequisites
      apt-get update
      apt-get install -y ca-certificates curl gnupg lsb-release
      
      # Add Docker's official GPG key
      mkdir -p /etc/apt/keyrings
      curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
      
      # Set up the repository
      echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
      
      # Install Docker Engine & Docker Compose Plugin
      apt-get update
      apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
      
      # Add vagrant user to docker group (so you don't need 'sudo' every time)
      usermod -aG docker vagrant
    SHELL
  end
end