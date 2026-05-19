# How to Use the MongoDB Plug-in

## Plugin Description

This plug-in is used to automatically deploy and manage MongoDB databases on openEuler. It provides the following functions:

- Automatically installing MongoDB
- Configuring MongoDB services
- Managing MongoDB services (starting, stopping, and viewing the status)
- Uninstalling MongoDB

## Supported Operations

- `install`: installs and configures MongoDB.
- `uninstall`: uninstalls MongoDB.
- `start`: starts MongoDB services.
- `stop`: stops MongoDB services.
- `status`: checks the MongoDB service status.

## Configuration Description

Configure the following parameters in the `config.yaml` file.

| Parameter| Description| Default Value|
|------|------|--------|
| `mongodb_version` | MongoDB version| 7.0 |
| `mongodb_install_path` | MongoDB installation path| /usr/local/mongodb |
| `mongodb_data_path` | MongoDB data directory| /var/lib/mongodb |
| `mongodb_log_path` | MongoDB log directory| /var/log/mongodb |
| `mongodb_port` | MongoDB port| 27017 |
| `mongodb_bind_ip` | MongoDB bound IP address| 127.0.0.1 |
| `mongodb_user` | MongoDB user| mongodb |
| `mongodb_password` | MongoDB password| ****** |
| `mongodb_database` | MongoDB database| admin |
| `download_timeout` | Download timeout (s)| 600 |
| `download_retry` | Download retry attempts| 3 |
| `install_mode` | Installation mode (repo/source)| repo |
| `enable_auth` | Whether to enable authentication| false |

## Examples

### Installing MongoDB

```bash
oedp run install
```

### Starting MongoDB Services

```bash
oedp run start
```

### Stopping MongoDB Services

```bash
oedp run stop
```

### Checking the Status of MongoDB Services

```bash
oedp run status
```

### Uninstalling MongoDB

```bash
oedp run uninstall
```

## Precautions

1. This plug-in requires the root permission.
2. By default, MongoDB is installed from the official MongoDB repository.
3. To enable authentication, set `enable_auth: true` in the `config.yaml` file.
4. After the installation is complete, the MongoDB service automatically starts and is set to start upon system boot.
5. This plug-in applies to openEuler 24.03-LTS and later versions.

## Troubleshooting

- If the installation fails, check whether the network connection is normal.
- If the service fails to start, check the `/var/log/mongodb/mongod.log` file.
- If the port is occupied, modify the `mongodb_port` parameter in the `config.yaml` file.

## Version History

- v1.0.0: initial version, which supports the installation and management of MongoDB 7.0.
