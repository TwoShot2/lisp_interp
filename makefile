project2: Project2.py
	python3 -m py_compile $<
	mv __pycache__/*.pyc .
	chmod +x *.pyc
	mv *.pyc lisp.pyc
	rm -rf __pycache__
