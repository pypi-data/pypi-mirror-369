from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("gerador-api-segura-v3")
except PackageNotFoundError:
    __version__ = "0.1.5"  # mantenha em sincronia ou use Hatch dynamic version
