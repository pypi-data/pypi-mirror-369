# PyTLS-CA

PyTLS-CA is a Python application that quickly creates self-signed TLS certificates for your local development environment.

## Install

You can install PyTLS-CA using pip:

```sh
pip install pytls-ca
```

## Usage

You can specify options like the CA name, the services for which to generate certificates, and the output directory. For example:

```sh
pytls -n 'My Custom CA' -s example.com -s api.example.com -d './certs'
```

If you have existing CA certificates, you can specify the paths to the CA certificate and key.

```sh
pytls --ca-cert './certs/ca.crt' --ca-key './certs/ca.key' -s example.com -s api.example.com
```

You can verify your certificate information with openssl:

```sh
openssl x509 -noout -text -in ./certs/example.com.crt
```

## Options

- `-n`, `--ca-name`: The subject for the CA certificate. Defaults to `PyTLS CA`.
- `-s`, `--services`: The services for which to generate certificates. Can be specified multiple times for multiple services.
- `-d`, `--output-directory`: The directory in which to save the generated certificates. Defaults to `./certificates`.
- `--ca-cert`: The path to an existing CA certificate. If specified, the CA certificate will be used to sign the generated certificates.
- `--ca-key`: The path to an existing CA key. If specified, the CA key will be used to sign the generated certificates.
- `-h`, `--help`: Show the help message and exit.

# Development

This project uses [Poetry](https://python-poetry.org/) for dependency management. To install the project and its dependencies, run:

```sh
poetry install
```

This project uses [Ruff](https://docs.astral.sh/ruff/) for linting and code formatting.

### Publishing

To publish a new version of the package, run:

```sh
poetry config pypi-token.pypi <token>
poetry publish --build
```