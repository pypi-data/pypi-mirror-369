from setuptools import setup

setup(
    capnpy_schemas=["src/simpleros/msg/std_msg.capnp"],
    capnpy_options={"pyx": False, "convert_case": False, "text_type": "unicode"},
)
