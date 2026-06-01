# How to Use the RavenDB Plug-in

## Plugin Description

This plug-in is used to automatically deploy and manage RavenDB databases on openEuler. It provides the following functions:

- Automatically installing RavenDB
- Configuring RavenDB services
- Managing RavenDB services (starting, stopping, and viewing the status)
- Uninstalling RavenDB

## Supported Operations

- `install`: installs and configures RavenDB.
- `uninstall`: uninstalls RavenDB.
- `start`: starts RavenDB services.
- `stop`: stops RavenDB services.
- `status`: checks the RavenDB service status.

## Configuration Description

Configure the following parameters in the `config.yaml` file.

| Parameter| Description| Default Value|
|------|------|--------|
| `ravendb_version` | RavenDB version| 6.0 |
| `ravendb_install_path` | RavenDB installation path| /usr/local/ravendb |
| `ravendb_data_path` | RavenDB data directory| /var/lib/ravendb |
| `ravendb_log_path` | RavenDB log directory| /var/log/ravendb |
| `ravendb_port` | RavenDB HTTP port| 8080 |
| `ravendb_management_port` | RavenDB management port| 38888 |
| `ravendb_bind_ip` | RavenDB bound IP address| 127.0.0.1 |
| `ravendb_user` | RavenDB user| ravendb |
| `ravendb_password` | RavenDB password| ****** |
| `ravendb_cluster_name` | RavenDB cluster name| RavenDB-Cluster |
| `download_timeout` | Download timeout (s)| 600 |
| `download_retry` | Download retry attempts| 3 |
| `install_mode` | Installation mode (direct)| direct |
| `enable_auth` | Whether to enable authentication| false |

## Example

### Installing RavenDB

```bash
oedp run install
```

### Starting RavenDB Services

```bash
oedp run start
```

### Stopping RavenDB Services

```bash
oedp run stop
```

### Checking the RavenDB Service Status

```bash
oedp run status
```

### Uninstalling RavenDB

```bash
oedp run uninstall
```

## Precautions

1. This plug-in requires the root permission.
2. RavenDB requires the Java 11 environment, which will be automatically installed by the plug-in.
3. By default, the installation package is downloaded from the official RavenDB website.
4. After the installation is complete, the RavenDB service automatically starts and is set to start upon system boot.
5. Visit <http://localhost:8080>
6. This plug-in applies to openEuler 24.03-LTS and later versions.

## Troubleshooting

- If the installation fails, check whether the network connection is normal.
- If the service fails to start, check the log file under `/var/log/ravendb`.
- If the port is occupied, modify the port parameter in the `config.yaml` file.
- If the Java environment is faulty, ensure that Java 11 has been correctly installed.

## Version History

- v1.0.0: initial version, which supports the installation and management of RavenDB 6.0.
