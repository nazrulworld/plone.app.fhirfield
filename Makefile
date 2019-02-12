mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
current_dir := $(dir $(mkfile_path))
current_dir_name := $(notdir $(patsubst %/,%,$(current_dir)))
esdata_dir := $(current_dir)var/esdata/data
es_version := 6.6.0


run-es:
	docker run --rm -v $(esdata_dir):/usr/share/elasticsearch/data -p 127.0.0.1:9200:9200 --name elasticsearch_ff -e "network.publish_host=127.0.0.1" -e "transport.publish_port=9200" -e "discovery.type=single-node" elasticsearch:$(es_version)
stop-all:
	docker kill $$(docker ps -q)

clean-es:
	curl -XDELETE 127.0.0.1:9200/_all