
publish: 
	export ASTA_SUMMARIZER_VERSION=$$(cat version.txt) ; \
	git tag v$$ASTA_SUMMARIZER_VERSION ; \
	git push origin --tags ; \
	bash publish.sh ; \