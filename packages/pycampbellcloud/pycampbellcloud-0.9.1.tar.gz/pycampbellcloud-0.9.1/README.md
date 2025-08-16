# pycampbellcloud

**_pycampbellcloud_** is a Python client library designed to provide a clean, object-oriented interface to the Campbell Cloud REST API. It abstracts away HTTP requests and authentication details, allowing you to easily access, manipulate, and manage monitoring data from [Campbell Cloud](https://campbell-cloud.com/).

## Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [Roadmap](#roadmap)
- [API Reference](#api-reference)

## Features

- Easy-to-use object-oriented interface
- Simplified authentication and session management
- Access to all endpoints of the Campbell Cloud API
- Support for data retrieval, manipulation, and management

## Installation

You can install `pycampbellcloud` using pip:

```bash
pip install pycampbellcloud
```

## Usage

Here's a quick example of how to use `pycampbellcloud`:
```python
from pycampbellcloud import CampbellCloud

# Initialize the client
client = CampbellCloud('your_organization_id', 'your_username', 'your_password')

# Fetch all datapoints of an asset
asset_data = client.get_datapoints("asset_id", datatables=["ExampleTable"], fieldnames=["ExampleFieldName"],
                                   start_epoch="0000000000000", end_epoch="9999999999999")

# print all datapoints
print(asset_data)
```

## Roadmap

☐ Document metadata parameters for all applicable endpoints

☐ Thorough code snippets and documentation pages in GitHub Wiki

## API Reference

For detailed information on the available methods and classes, please refer to the [API documentation](https://us-west-2.campbell-cloud.com/api/v1/docs/).
