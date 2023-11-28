#/bin/bash

kafka-topics --bootstrap-server localhost:9093 --create --topic sensors-raw --command-config client-properties/adminclient.properties --partitions 1 --replication-factor 1

kafka-acls --bootstrap-server localhost:9093 --command-config client-properties/adminclient.properties --topic sensors-raw --allow-principal User:producer --producer --add

kafka-acls --bootstrap-server localhost:9093 --command-config client-properties/adminclient.properties --topic sensors-raw --allow-principal User:consumer --consumer --add --group "my-group-0"
kafka-acls --bootstrap-server localhost:9093 --command-config client-properties/adminclient.properties --topic sensors-raw --allow-principal User:consumer --consumer --add --group "my-group-1"

kafka-topics --bootstrap-server localhost:9093 --create --topic sensors-clean --command-config client-properties/adminclient.properties --partitions 1 --replication-factor 1

kafka-acls --bootstrap-server localhost:9093 --command-config client-properties/adminclient.properties --topic sensors-clean --allow-principal User:producer --producer --add

kafka-acls --bootstrap-server localhost:9093 --command-config client-properties/adminclient.properties --topic sensors-clean --allow-principal User:consumer --consumer --add --group "my-group-0"
kafka-acls --bootstrap-server localhost:9093 --command-config client-properties/adminclient.properties --topic sensors-raw --allow-principal User:consumer --producer --add --group "my-group-1"
kafka-acls --bootstrap-server localhost:9093 --command-config client-properties/adminclient.properties --topic sensors-clean --allow-principal User:consumer --consumer --add --group "my-group-2"
