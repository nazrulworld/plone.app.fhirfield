current_dir := $(notdir $(patsubst %/,%,$(dir $(mkfile_path))))


run-es:
	docker run --rm -p 127.0.0.1:9200:9200 --name elasticsearch_ff elasticsearch:2.4.6
