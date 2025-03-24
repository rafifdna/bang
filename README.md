# Bang: AWS IAM Access Key Rotation Tool

Bang automates the AWS IAM access key rotation process to help maintain good security hygiene. AWS IAM users can have a maximum of two access keys at any time, and regularly rotating these keys reduces the risk of compromised credentials.


## Quick Start Guide

### Installation

```bash
# Clone this repository
git clone https://github.com/yourusername/bang.git
cd bang

# Install dependencies
pip install boto3

# Make the script executable
chmod +x main.py
```

### Basic Usage

The simplest way to use Bang is with default settings:

```bash
./main.py
```

This command will:
* Detect your current AWS user
* Rotate the access keys for that user
* Update your default profile in ~/.aws/credentials
* Deactivate your old key
* Schedule the old key for deletion after 7 days

## Common Examples

1. Rotate keys for a specific profile:

```bash
./main.py --profile production
```

2. Rotate keys for a specific user:

```bash
./main.py --user admin-user
```

3. Delete old keys immediately with no grace period:

```bash
./main.py --grace-period 0
```

4. Force rotation when a user already has two keys:

```bash
./main.py --force
```

## Automating Key Rotation

You can set up scheduled key rotation using cron or other scheduling tools:

```bash
# Example cron entry to rotate keys every 90 days
0 0 1 */3 * /path/to/main.py --profile default >> /var/log/key-rotation.log 2>&1
```