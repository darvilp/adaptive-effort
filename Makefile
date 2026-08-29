.PHONY: test validate package clean

test:
	python3 -m unittest discover -s tests -v

validate:
	python3 scripts/validate.py

package: validate test
	mkdir -p dist
	python3 scripts/package.py --output dist/adaptive-effort-plugin-0.1.1.zip

clean:
	rm -rf dist __pycache__ tests/__pycache__
