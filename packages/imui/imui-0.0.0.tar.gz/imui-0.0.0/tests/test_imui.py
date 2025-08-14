import imui
from imui import version

class TestClass:
    def test_version(self):
        assert imui.__version__ == version.__version__

    def test_import_extension(self):
        success = True
        try:
            from imgui import _C
        except:
            success = False
        assert success