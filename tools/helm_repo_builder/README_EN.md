# Helm Repository Mirror Builder

## 1. Features

This tool is designed to quickly build local Helm repository mirrors, improving download speed and stability during Helm chart installations, thereby optimizing the overall Helm user experience.

## 2. Usage

Run the following command to quickly build a repository mirror:

```shell
./helm-repo-builder.py <repo-url> [options]
python3 helm-repo-builder.py <repo-url> [options]

```

### Arguments

* `repo-url`: The URL of the source repository, identical to the URL used in `helm repo add`.

### Options

* `--url URL`: Specifies the base URL for the mirrored repository.
  * Default: Empty. **Note**: This will omit the `urls` field in the generated `index.yaml`, forcing Helm to locate `.tgz` files using relative paths.

* `--path PATH`: Specifies the local root directory where Helm charts will be downloaded and stored.
  * Default: Current directory.

* `--prefix PREFIX`: Specifies a common prefix to strip from the source download URLs. The tool will build the local directory tree based on the remaining path suffix.
  * Default: Automatically detects the common prefix.

* `--re-download`: Forces the re-download of all files.
  * Default: Disabled. Skips downloading if the file already exists locally and passes the checksum verification.

* `--no-index`: Only downloads the `.tgz` files without generating or updating the `index.yaml` file.
  * Default: Disabled.

* `--only-index`: Generates the `index.yaml` file based on the existing local directory structure without downloading any `.tgz` files.
  * Default: Disabled.

* `--new-index`: Forces the tool to overwrite the existing `index.yaml` file when generating a new one.
  * Default: Disabled. By default, new chart records are merged into the existing `index.yaml`.

* `--retry N`: Specifies the maximum number of retries for failed downloads.
  * Default: 5.
