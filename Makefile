
MKDV_DIR:=$(dir $(abspath $(lastword $(MAKEFILE_LIST))))
ifeq (,$(PACKAGES_DIR))
  PACKAGES_DIR := $(MKDV_DIR)/packages
endif

export PACKAGES_DIR

pdf : 
	$(PACKAGES_DIR)/python/bin/sphinx-build -M latexpdf \
		$(MKDV_DIR)/doc/source \
		build

html : 
	$(PACKAGES_DIR)/python/bin/sphinx-build -M html \
		$(MKDV_DIR)/doc/source \
			build

clean :
	rm -rf build 

