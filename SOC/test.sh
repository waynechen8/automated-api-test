#!/bin/bash
#Run(Mount Volume, Stress)

#Create
/home/jmeter/apache-jmeter-4.0/bin/jmeter -n -t /home/jmeter/NCHC_Swagger/WL-A01/SOC/WL-A01_SOC_Create.jmx -l /home/jmeter/NCHC_Swagger/WL-A01/SOC/WL-A01_SOC_Create.jtl

chmod 400 /home/jmeter/NCHC_Swagger/WL-A01/SOC/keypairs.pem
remoteVmIp="$(cat /home/jmeter/NCHC_Swagger/WL-A01/SOC/wla01.properties | sed -n '3p' | cut -d "=" -f2)"
ssh -i /home/jmeter/NCHC_Swagger/WL-A01/SOC/keypairs.pem ubuntu@$remoteVmIp << EOF
  sudo apt-get update
  sudo apt-get -y install stress git

  sudo mkfs.ext4 /dev/vdb
  sudo mkdir /home/ubuntu/volume
  sudo mount /dev/vdb  /home/ubuntu/volume

  sudo git clone https://github.com/tensorflow/tensorflow.git /home/ubuntu/volume/tensorflow

  stress -c 16 --timeout 10m --backoff 100000000

  exit
EOF

#Run(JMX)
/home/jmeter/apache-jmeter-4.0/bin/jmeter -n -t /home/jmeter/NCHC_Swagger/WL-A01/SOC/WL-A01_SOC_Run.jmx -l /home/jmeter/NCHC_Swagger/WL-A01/SOC/WL-A01_SOC_Run.jtl

#Stop
/home/jmeter/apache-jmeter-4.0/bin/jmeter -n -t /home/jmeter/NCHC_Swagger/WL-A01/SOC/WL-A01_SOC_Stop.jmx -l /home/jmeter/NCHC_Swagger/WL-A01/SOC/WL-A01_SOC_Stop.jtl

#Resume
/home/jmeter/apache-jmeter-4.0/bin/jmeter -n -t /home/jmeter/NCHC_Swagger/WL-A01/SOC/WL-A01_SOC_Resume.jmx -l /home/jmeter/NCHC_Swagger/WL-A01/SOC/WL-A01_SOC_Resume.jtl
