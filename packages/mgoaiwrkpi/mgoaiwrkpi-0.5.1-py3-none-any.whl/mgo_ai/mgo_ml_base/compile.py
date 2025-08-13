from distutils.core import setup
from distutils.extension import Extension
from Cython.Distutils import build_ext
ext_modules = [
    Extension("local_models", ["local_models.py"], extra_compile_args=["-g0"]),
    Extension("mgo_trainer", ["mgo_trainer.py"], extra_compile_args=["-g0"]),
    Extension("format_map", ["format_map.py"], extra_compile_args=["-g0"]),
    Extension("formatter", ["formatter.py"], extra_compile_args=["-g0"]),

]
setup(
    name='mgo_ml_base',
    cmdclass={'build_ext': build_ext},
    ext_modules=ext_modules
)