# Bang: AWS IAM Access Key Rotation Tool

A simple yet powerful Python utility for automating the rotation of AWS IAM access keys following security best practices.

## Overview

Bang automates the AWS IAM access key rotation process to help maintain good security hygiene. AWS IAM users can have a maximum of two access keys at any time, and regularly rotating these keys reduces the risk of compromised credentials.

The tool performs the following operations:

1. Creates a new access key for the specified IAM user
2. Updates the AWS credentials file with the new key
3. Waits for the new key to propagate in AWS systems
4. Deactivates the old access key
5. Optionally deletes the old key after a specified grace period

## Quick Start Guide

### Installation

```bash
# Clone this repository
git clone https://github.com/yourusername/bang.git
cd bang

# Install dependencies
pip install boto3

# Make the script executable
chmod +x bang.py