"""Generates CA and server certificates.
\nExample:
\n  pytls -n 'My CA' -s example.dev -s api.example.dev -d ./certs
"""
import os

import click

from pytls_ca.crypt import create_cert_file, create_key_file, generate_ca_cert, generate_server_cert, load_ca_cert


@click.command(help=__doc__)
@click.option("-n", "--ca-name", default="PyTLS CA", help="The subject for the CA certificate.")
@click.option("-s", "--services", multiple=True, help="The services for which to generate certificates.")
@click.option("--ca-cert", default=None, help="The path to an existing CA certificate file. (ex: ca.crt)")
@click.option("--ca-key", default=None, help="The path to an existing CA key file. (ex: ca.key)")
@click.option("-d", "--output-directory", default="certs", help="The directory to write the certificates to.")
def cli(ca_name, services, ca_cert, ca_key, output_directory):
    # Create the output directory if it doesn't exist
    os.makedirs(output_directory, exist_ok=True)

    if ca_cert and ca_key:
        # Load the existing CA certificate and key
        ca_key, ca_cert = load_ca_cert(ca_cert, ca_key)
    else:
        # Generate the CA certificate
        ca_key, ca_cert = generate_ca_cert(subject=ca_name)
        create_cert_file(ca_cert, "ca", output_directory)
        create_key_file(ca_key, "ca", output_directory)

    # Generate the server certificates for each service
    for service in services:
        # Handle wildcard services
        # If service starts with '*.', use base domain for CN and include wildcard in SANs
        if service.startswith('*.'):
            base_domain = service[2:]
            cn = base_domain
            sans = [service, base_domain]
            filename = service.replace('*', 'wildcard')
        else:
            cn = service
            sans = [service]
            filename = service

        service_key, service_cert = generate_server_cert(
            ca_key=ca_key,
            ca_cert=ca_cert,
            subject=cn,
            sans=sans,
        )

        # Write the certificate and key to files (map '*' to 'wildcard' in filenames)
        create_cert_file(service_cert, filename, output_directory)
        create_key_file(service_key, filename, output_directory)

    click.echo("Certificates created in: " + os.path.abspath(output_directory))


if __name__ == "__main__":
    cli()
