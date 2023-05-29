# Installation build file for Magicor.
#
# Copyright 2006  Peter Gebauer. Licensed as Public Domain.
# (see LICENSE for more info)
#
# Valid targets:
#
# install			Install everything in specified paths.
# uninstall			Remove everything from specified paths. (use with care!)
# clean				Clean the build root from temporary files.
# dist				Create source and data tarballs.

# Do not change this unless you know what you're doing.
PYTHON_VERSION=$(shell python -c "import sys; print(sys.version[:3])")
#PYTHON_VERSION=2.4

# The prefix is added as a prefix to all other paths as default.
PREFIX=/usr/local
# Where the magicor package will be installed, including final directory.
PYTHON_LIB=$(PREFIX)/lib/python$(PYTHON_VERSION)/site-packages/magicor
# Where the executable scripts will be installed.
BIN_PATH=$(PREFIX)/games
# Where the shared data will be stored.
SHARE_PATH=$(PREFIX)/share/magicor
# Where to find the system-wide config file.
CONFIG=$(PREFIX)/etc
# Docbook XSL stylesheet to use
DOCBOOK_STYLESHEET=/usr/share/xml/docbook/stylesheet/nwalsh/xhtml/docbook.xsl
# Options (string parameters) passed to the XSLT processor
#DOCBOOK_OPTIONS=--stringparam name value
# Docbook processing command
DOCBOOK_PROCESS=xsltproc -o $@ $(DOCBOOK_OPTIONS) $(DOCBOOK_STYLESHEET) $<

# For developers, change version with Magicor version number
VERSION=1.1


.PHONY: all
all:
	@echo "Environment:"
	@echo "Detected Python     $(PYTHON_VERSION)"
	@echo "Library path set to $(PYTHON_LIB)"
	@echo "Binary path set to  $(BIN_PATH)"
	@echo "Data path set to    $(SHARE_PATH)"
	@echo "Default config in   $(CONFIG)"
	@echo
	@echo "Docbook process (optional doc-target):"
	@echo $(DOCBOOK_PROCESS)
	@echo
	@echo "Valid targets: install, uninstall, clean, doc"
	@echo

.PHONY: install
install:
	@if [ -z "$(PYTHON_VERSION)" ]; then echo "Could not detect Python version, please edit the Makefile and set PYTHON_VERSION manually"; exit 1; fi
	mkdir -p $(PYTHON_LIB)
	cp -fr magicor/* $(PYTHON_LIB)
	cat Magicor.py | python scripts/replacer.py "###CONFIG_PATH###" $(CONFIG)/magicor.conf > $(BIN_PATH)/magicor
	cat etc/magicor.conf | python scripts/replacer.py "###SHARE_PATH###" $(SHARE_PATH) > $(CONFIG)/magicor.conf
	cat Magicor-LevelEditor.py | python scripts/replacer.py "###CONFIG_PATH###" $(CONFIG)/magicor-editor.conf > $(BIN_PATH)/magicor-editor
	cat etc/magicor-editor.conf | python scripts/replacer.py "###SHARE_PATH###" $(SHARE_PATH) > $(CONFIG)/magicor-editor.conf
	chmod a+x $(BIN_PATH)/magicor
	chmod a+x $(BIN_PATH)/magicor-editor
	mkdir -p $(SHARE_PATH)
	cp -fr data/* $(SHARE_PATH)
	@echo "Done. If everything wen't well you can now run '$(BIN_PATH)/Magicor'"

.PHONY: uninstall
uninstall:
	rm -Rf $(PYTHON_LIB)
	rm -Rf $(SHARE_PATH)
	rm -f $(BIN_PATH)/magicor $(BIN_PATH)/magicor-editor

.PHONY: clean
clean:
	find . -name "*.pyc" | xargs rm -f
	find . -name "*.bak" | xargs rm -f
	find . -name "*~" | xargs rm -f
	rm -Rf dist
	rm -f magicor-*.tar.gz
	rm -f *.cdbs-config_list

.PHONY: dist
dist:
	rm -Rf dist
	mkdir -p dist/magicor-$(VERSION)
	rsync -Cavr --include=*.py magicor dist/magicor-$(VERSION)/
	rsync -Cavr --include=*.py scripts dist/magicor-$(VERSION)/
	cp -f *.py dist/magicor-$(VERSION)/
	rsync -Cavr etc dist/magicor-$(VERSION)/
	cp -f README INSTALL LICENSE Makefile dist/magicor-$(VERSION)/
	tar -cvzf magicor-source-$(VERSION).tar.gz -C dist magicor-$(VERSION)	
	rsync -Cavr data dist/magicor-$(VERSION)/
	tar -cvzf magicor-data-$(VERSION).tar.gz -C dist magicor-$(VERSION)/data

.PHONY: doc
doc: doc/manual.xhtml

mdoc/manual.xhtml: doc/manual.docbook
	$(DOCBOOK_PROCESS)
