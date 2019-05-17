mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
current_dir := $(dir $(mkfile_path))
current_dir_name := $(notdir $(patsubst %/,%,$(current_dir)))
es_version := 6.3.0


run-es:
	docker run --rm \
	-e "cluster.name=docker-cluster" \
	-e "ES_JAVA_OPTS=-Xms1024m -Xmx1024m" \
	-e "cluster.routing.allocation.disk.threshold_enabled=false" \
	-p 127.0.0.1:9200:9200 \
	--name elasticsearch_ff0 \
	docker.elastic.co/elasticsearch/elasticsearch-oss:$(es_version)


stop-all:
	docker kill $$(docker ps -q)

clean-es:
	curl -XDELETE 127.0.0.1:9200/_all

es-health:
	curl -XGET http://127.0.0.1:9200/_cat/health

set-vm-map-count:
	sysctl -w vm.max_map_count=262144

# curl -XPUT -H "Content-Type: application/json" http://localhost:9200/_all/_settings -d '{"index.blocks.read_only_allow_delete": null}'
