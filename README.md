# NGINX Reverse Proxy & Load Balancer

A containerized web application demonstrating how NGINX acts as an HTTPS reverse proxy and distributes incoming requests across multiple Python backend services using Docker Compose.

## Overview

This project demonstrates a basic web application architecture in which NGINX acts as the single entry point for client requests, terminates HTTPS connections, and distributes traffic across three Python backend containers.

The environment is built with Docker Compose, making it easy to run and test locally.

## Features

* **Reverse Proxy:** NGINX forwards incoming requests to Python backend services.
* **Load Balancing:** Distributes requests across three backend instances using NGINX's default round-robin algorithm.
* **HTTPS:** Terminates TLS connections at NGINX using a locally generated self-signed certificate.
* **HTTP-to-HTTPS Redirection:** Redirects HTTP requests to HTTPS.
* **Containerization:** Packages the Python application into a Docker image.
* **Docker Networking:** Allows NGINX to communicate with backend containers through an internal bridge network.
* **Private Backend Services:** Backend ports are not published directly on the host.
* **API Testing:** Uses pytest and requests to test HTTPS responses, HTTP redirection, and load balancing.

## Architecture

```text
                  Client / Web Browser
                           |
                           |
                   HTTP :80 or HTTPS :443
                           |
                           v
                 +--------------------+
                 |    NGINX Proxy     |
                 |                    |
                 | HTTP -> HTTPS      |
                 | TLS Termination   |
                 | Load Balancing    |
                 +--------------------+
                           |
                   Docker Bridge Network
                           |
             +-------------+-------------+
             |             |             |
             v             v             v
       +-----------+ +-----------+ +-----------+
       |   app1    | |   app2    | |   app3    |
       | Python    | | Python    | | Python    |
       | :8000     | | :8000     | | :8000     |
       +-----------+ +-----------+ +-----------+
             |             |             |
             +-------------+-------------+
                           |
                     HTML Response
                           |
                           v
                      NGINX Proxy
                           |
                           v
                    Client / Browser
```

### Request flow

1. A client sends an HTTP request to port `80` or an HTTPS request to port `443`.
2. NGINX redirects HTTP requests to HTTPS.
3. For HTTPS requests, NGINX handles TLS termination and decrypts the incoming connection.
4. NGINX selects a backend using round-robin load balancing.
5. The selected Python service processes the request and generates an HTML response.
6. NGINX forwards the response to the client over HTTPS.

### Port mapping

| Port   | Component       | Purpose                                                        |
| ------ | --------------- | -------------------------------------------------------------- |
| `80`   | NGINX           | Receives HTTP requests and redirects them to HTTPS             |
| `443`  | NGINX           | Receives HTTPS requests and terminates TLS                     |
| `8000` | Python backends | Internal HTTP communication between NGINX and backend services |

**Note:** Port `8000` is not published to the host. The backend services are reachable by NGINX through the Docker network using service names such as `app1:8000`.

## Technologies Used

| Technology     | Purpose                                            |
| -------------- | -------------------------------------------------- |
| NGINX          | Reverse proxy, TLS termination, and load balancing |
| Python         | Backend HTTP server                                |
| Docker         | Containerizes the application                      |
| Docker Compose | Defines and runs the multi-container environment   |
| HTML           | Backend response template                          |
| OpenSSL        | Generates a local self-signed TLS certificate      |
| pytest         | Test framework                                     |
| requests       | Sends HTTP and HTTPS requests during testing       |

## Project Structure

```text
nginx-reverse-proxy-load-balancer/
├── app/
│   ├── Dockerfile
│   ├── server.py
│   └── index.html
├── nginx/
│   └── nginx.conf
├── tests/
│   └── test_api.py
├── .gitignore
├── compose.yaml
├── requirements-dev.txt
└── README.md
```

## Prerequisites

Install the following tools before running the project:

* [Docker Desktop](https://www.docker.com/products/docker-desktop/)
* Docker Compose (included with current Docker Desktop installations)
* [OpenSSL](https://www.openssl.org/) for generating the local certificate
* Python 3 for running the test suite locally
* Git, if you want to clone or contribute to the repository

## Run Locally

### 1. Clone the repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd nginx-reverse-proxy-load-balancer
```

Replace `<YOUR_GITHUB_REPOSITORY_URL>` with your repository's clone URL.

### 2. Generate a local TLS certificate

Create the certificate directory:

**PowerShell:**

```powershell
New-Item -ItemType Directory -Force certs
```

Generate a self-signed certificate and private key using OpenSSL:

```powershell
openssl req -x509 -nodes -days 365 -newkey rsa:2048 `
  -keyout certs/nginx-selfsigned.key `
  -out certs/nginx-selfsigned.crt `
  -subj "/CN=localhost" `
  -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"
```

The generated certificate and private key are used for local development. The `certs/` directory is excluded from Git.

### 3. Start the application

From the repository root, run:

```bash
docker compose up -d --build
```

Docker Compose builds the Python application image, starts the three backend services, and starts NGINX.

### 4. Check the containers

```bash
docker compose ps
```

View the logs if needed:

```bash
docker compose logs
```

### 5. Access the application

Open the following address in your browser:

**https://localhost**

Because the certificate is self-signed, your browser may display a certificate warning. This is expected for the local development setup.

To test HTTP-to-HTTPS redirection, open:

**http://localhost**

### 6. Verify load balancing

Run the following PowerShell command to send multiple independent requests:

```powershell
1..12 | ForEach-Object {
    $response = curl.exe -sk https://localhost/
    $app = [regex]::Match(
        $response,
        'Welcome to ([^<]+)'
    ).Groups[1].Value

    Write-Output "Request $_ -> $app"
}
```

The responses should include `app1`, `app2`, and `app3`, demonstrating that requests are distributed across the backend services.

## Run Tests

Install the development dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

Make sure the Docker Compose environment is running, then execute:

```bash
python -m pytest -v
```

The tests cover:

* HTTP-to-HTTPS redirection.
* Successful HTTPS requests.
* Load balancing across the backend services, if the corresponding test is included in `tests/test_api.py`.

The local tests use certificate verification disabled for the self-signed development certificate. This is intended only for the local lab.

## Useful Commands

| Command                              | Purpose                                    |
| ------------------------------------ | ------------------------------------------ |
| `docker compose up -d --build`       | Build and start the environment            |
| `docker compose ps`                  | Check container status                     |
| `docker compose logs -f`             | Follow container logs                      |
| `docker compose logs nginx`          | View NGINX logs                            |
| `docker compose logs app1 app2 app3` | View backend logs                          |
| `docker compose exec nginx nginx -t` | Validate NGINX configuration               |
| `docker compose exec nginx nginx -T` | Inspect the active NGINX configuration     |
| `docker compose down`                | Stop and remove the containers and network |

## Security Considerations

* The self-signed certificate is intended for local development only.
* Private keys and local certificates are excluded from version control.
* Backend services are not published directly on host ports.
* The Docker bridge network provides connectivity between NGINX and the backend containers.
* Certificate verification is disabled in the local HTTPS tests; do not use this setting for production clients.

## Limitations

This project is a learning lab, not a production-hardened deployment.

It currently uses a simple Python HTTP server and a self-signed certificate. Production deployments would require additional considerations, including trusted TLS certificates, application health checks, hardened container configuration, monitoring, and more comprehensive automated testing.

## Learning Outcomes

Through this project, I explored:

* Reverse proxy architecture and request routing.
* Round-robin load balancing.
* HTTPS and TLS termination.
* Docker image building and multi-container orchestration.
* Docker bridge networking and service-name resolution.
* HTTP-to-HTTPS redirection.
* Basic API testing and troubleshooting.

## License

This project is available under the license specified in the repository, if one is added.