build/Project2.py: src/Project2.py
	@mkdir -p build
	python3 -m py_compile $<

# Clean up compiled files
clean:
	@rm -rf build
