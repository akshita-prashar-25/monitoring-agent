import psutil
import requests
import time
import socket
import json
import os


# =========================
# BACKEND CONFIGURATION
# =========================

backend_url = os.getenv(
    "BACKEND_URL",
    "http://localhost:8080"
)

registration_url = (
    f"{backend_url}/api/agents/register"
)

metrics_url = (
    f"{backend_url}/api/metrics"
)


# =========================
# AGENT CONFIGURATION
# =========================

agent_name = "Windows Monitoring Agent"

# =========================
# CREDENTIAL FILE
# =========================

credential_file = "agent_credentials.json"


# =========================
# GET MACHINE INFORMATION
# =========================

hostname = socket.gethostname()


try:

    ip_address = socket.gethostbyname(
        hostname
    )

except Exception:

    ip_address = "127.0.0.1"


# =========================
# REGISTER NEW AGENT
# =========================

def register_agent():

    print(
        "\nRegistering agent with Spring Boot..."
    )


    registration_data = {

        "agentName": agent_name,

        "hostname": hostname,

        "ipAddress": ip_address

    }


    try:

        response = requests.post(

            registration_url,

            json=registration_data,

            timeout=5

        )


        if not response.ok:

            print(
                "\nAgent registration failed."
            )

            print(
                "Status:",
                response.status_code
            )

            print(
                "Response:",
                response.text
            )

            return None


        agent_data = response.json()


        # =========================
        # SAVE CREDENTIALS
        # =========================

        credentials = {

            "agentId":
                agent_data["id"],

            "serverId":
                agent_data["serverId"],

            "apiKey":
                agent_data["apiKey"]

        }


        with open(
            credential_file,
            "w"
        ) as file:

            json.dump(
                credentials,
                file,
                indent=4
            )


        print(
            "\nAgent registered successfully!"
        )

        print(
            "Agent ID:",
            agent_data["id"]
        )

        print(
            "Server ID:",
            agent_data["serverId"]
        )

        print(
            "Status:",
            agent_data["status"]
        )

        print(
            "\nAgent credentials saved."
        )


        return credentials


    except requests.exceptions.RequestException as error:

        print(
            "\nCould not connect to Spring Boot."
        )

        print(
            "Error:",
            error
        )

        return None


# =========================
# LOAD EXISTING CREDENTIALS
# =========================

def load_credentials():

    if not os.path.exists(
        credential_file
    ):

        return None


    try:

        with open(
            credential_file,
            "r"
        ) as file:

            credentials = json.load(
                file
            )


        return credentials


    except Exception as error:

        print(
            "\nCould not read saved credentials."
        )

        print(
            "Error:",
            error
        )

        return None


# =========================
# START AGENT
# =========================

print(
    "\n=============================="
)

print(
    "Starting Monitoring Agent"
)

print(
    "=============================="
)


# =========================
# CHECK FOR SAVED CREDENTIALS
# =========================

credentials = load_credentials()


if credentials:

    print(
        "\nExisting agent credentials found."
    )

    print(
        "Using existing registration."
    )

    agent_id = credentials["agentId"]

    registered_server_id = (
        credentials["serverId"]
    )

    api_key = credentials["apiKey"]


else:

    print(
        "\nNo existing agent registration found."
    )


    credentials = register_agent()


    if credentials is None:

        print(
            "\nUnable to start monitoring agent."
        )

        exit()


    agent_id = credentials["agentId"]

    registered_server_id = (
        credentials["serverId"]
    )

    api_key = credentials["apiKey"]


# =========================
# DISPLAY AGENT INFORMATION
# =========================

print(
    "\n=============================="
)

print(
    "Agent Information"
)

print(
    "=============================="
)

print(
    "Agent ID:",
    agent_id
)

print(
    "Server ID:",
    registered_server_id
)

print(
    "Hostname:",
    hostname
)

print(
    "IP Address:",
    ip_address
)

print(
    "Status: ACTIVE"
)


# =========================
# NETWORK INITIAL VALUES
# =========================

previous_network = (
    psutil.net_io_counters()
)

previous_time = time.time()


# =========================
# MONITORING INTERVAL
# =========================

monitoring_interval = 10


# =========================
# AUTHENTICATION HEADER
# =========================

headers = {

    "X-API-Key": api_key

}


# =========================
# CONTINUOUS MONITORING
# =========================

while True:

    try:

        # =========================
        # CPU
        # =========================

        cpu_usage = (
            psutil.cpu_percent(
                interval=1
            )
        )


        # =========================
        # MEMORY
        # =========================

        memory_usage = (
            psutil.virtual_memory()
            .percent
        )


        # =========================
        # DISK
        # =========================

        disk_path = os.path.abspath(os.sep)

        disk_usage = (
            psutil.disk_usage(
            disk_path
        ).percent
)


        # =========================
        # NETWORK
        # =========================

        current_network = (
            psutil.net_io_counters()
        )

        current_time = time.time()


        bytes_sent = (
            current_network.bytes_sent
        )

        bytes_received = (
            current_network.bytes_recv
        )


        sent_difference = (

            current_network.bytes_sent
            -
            previous_network.bytes_sent

        )


        received_difference = (

            current_network.bytes_recv
            -
            previous_network.bytes_recv

        )


        time_difference = (

            current_time
            -
            previous_time

        )


        upload_speed = (

            sent_difference
            /
            time_difference

        )


        download_speed = (

            received_difference
            /
            time_difference

        )


        # =========================
        # SYSTEM UPTIME
        # =========================

        boot_time = (
            psutil.boot_time()
        )


        uptime_seconds = int(

            time.time()
            -
            boot_time

        )


        # =========================
        # UPDATE PREVIOUS VALUES
        # =========================

        previous_network = (
            current_network
        )

        previous_time = (
            current_time
        )


        # =========================
        # CREATE METRIC DATA
        # =========================

        metric_data = {

            "serverId":
                registered_server_id,

            "cpuUsage":
                cpu_usage,

            "memoryUsage":
                memory_usage,

            "diskUsage":
                disk_usage,

            "bytesSent":
                bytes_sent,

            "bytesReceived":
                bytes_received,

            "uploadSpeed":
                upload_speed,

            "downloadSpeed":
                download_speed,

            "uptimeSeconds":
                uptime_seconds

        }


        # =========================
        # SEND METRICS
        # =========================

        response = requests.post(

            metrics_url,

            json=metric_data,

            headers=headers,

            timeout=5

        )


        # =========================
        # DISPLAY DATA
        # =========================

        print(
            "\n=============================="
        )

        print(
            "Agent ID:",
            agent_id
        )

        print(
            "Server ID:",
            registered_server_id
        )

        print(
            "Metrics collected:"
        )

        print(
            "CPU:",
            cpu_usage,
            "%"
        )

        print(
            "Memory:",
            memory_usage,
            "%"
        )

        print(
            "Disk:",
            disk_usage,
            "%"
        )

        print(
            "Upload Speed:",
            round(
                upload_speed / 1024,
                2
            ),
            "KB/s"
        )

        print(
            "Download Speed:",
            round(
                download_speed / 1024,
                2
            ),
            "KB/s"
        )

        print(
            "Uptime:",
            uptime_seconds,
            "seconds"
        )

        print(
            "Spring Boot response:",
            response.status_code
        )


        if response.ok:

            print(
                "Metric sent successfully."
            )

        else:

            print(
                "Failed to send metric:"
            )

            print(
                response.text
            )


    except requests.exceptions.RequestException as error:

        print(
            "\nCould not connect to Spring Boot."
        )

        print(
            "Error:",
            error
        )


    except Exception as error:

        print(
            "\nMonitoring error:"
        )

        print(
            "Error:",
            error
        )


    print(
        f"\nNext check in "
        f"{monitoring_interval} seconds..."
    )


    time.sleep(
        monitoring_interval
    )