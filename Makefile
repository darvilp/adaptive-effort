.PHONY: test validate package-source package-submission package clean

test:
	PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v

validate:
	python3 scripts/validate.py

package-source: validate test
	mkdir -p dist
	python3 scripts/package.py --output dist/adaptive-effort-source-0.1.3.zip

package-submission: validate test
	mkdir -p dist
	python3 scripts/package_submission.py --output dist/adaptive-effort-plugin-0.1.3.zip

package: package-source package-submission

clean:
	rm -rf dist __pycache__ tests/__pycache__
