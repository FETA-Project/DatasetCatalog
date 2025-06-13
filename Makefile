PKGNAME=katoda
VERSION=$(shell grep -E '^VERSION =' app.py | cut -d'"' -f2)
RELEASE=1
RPMDIR=RPMBUILD

.PHONY: tar
tar:
	mkdir $(PKGNAME)-$(VERSION)
	cp *.py $(PKGNAME)-$(VERSION)
	cp Makefile $(PKGNAME).spec config.env.example analysis_example.toml requirements.txt $(PKGNAME)-$(VERSION)
	cp katoda.service katoda-jupyter.service $(PKGNAME)-$(VERSION)
	cp -r frontend/.output/public $(PKGNAME)-$(VERSION)/static
	tar -czf $(PKGNAME)-$(VERSION).tar.gz $(PKGNAME)-$(VERSION)
	rm -rf $(PKGNAME)-$(VERSION)

.PHONY: rpm
rpm: tar
	mkdir -p $(RPMDIR)/BUILD/ $(RPMDIR)/SRPMS/ $(RPMDIR)/RPMS/ $(RPMDIR)/SOURCES
	cp $(PKGNAME)-$(VERSION).tar.gz $(RPMDIR)/SOURCES
	rpmbuild -ba $(PKGNAME).spec --define "_topdir `pwd`/$(RPMDIR)" --define "_target_os linux";
	rm -rf ${PKGNAME}-${VERSION}.tar.gz

.PHONY: clean
clean:
	rm -rf ./$(RPMDIR) $(PKGNAME)-$(VERSION).tar.gz
