from setuptools import setup

installation_requirements = [
    "openai-agents==0.2.4",
    "loguru==0.7.3",
    "neo4j==5.28.1",
    "google-genai==1.12.1"
]

setup(
    version="0.19",
    name="freeflock-contraptions",
    description="A collection of contraptions",
    author="(~)",
    url="https://github.com/freeflock/contraptions",
    package_dir={"": "packages"},
    packages=["freeflock_contraptions"],
    install_requires=installation_requirements,
)
