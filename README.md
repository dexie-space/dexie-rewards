# Auto-Claim dexie rewards

[![PyPI version](https://badge.fury.io/py/dexie-rewards.svg)](https://badge.fury.io/py/dexie-rewards)
[![Python version](https://img.shields.io/pypi/pyversions/dexie-rewards.svg)](https://pypi.python.org/pypi/dexie-rewards)

dexie-rewards is a Python CLI helper tool designed automatically claim [dexie liquidity rewards](https://dexie.space/incentives) for offers created using the official Chia Wallet. The tool communicates locally with the Chia Wallet RPC, requests all created offers, and checks them for claimable rewards.

When rewards are claimed, a message from the input (maker) address of the offer is signed to prove ownership of the offer. The signature is then sent to dexie to claim the rewards. dexie distributes claimed rewards to the input (maker) address in batches approximately every 15 minutes.

## Example Output

```
❯ dexie rewards claim
╭──────────────────────────────────────────────┬───────────────╮
│                   Offer ID                   │ Rewards (DBX) │
├──────────────────────────────────────────────┼───────────────┤
│ 8Ya1mwC7Z8S4RhKhuJjKPH6mQVksz4Hah8JsZ5NjaBYY │         0.494 │
│ BZFXcbJM7oSMz9RatJpMBSD1Hmj4JWXHJE7DCBXDV8mJ │        21.854 │
│ CbdGX5KUHnHLbX8VSFPKTDcbK87NKUtQTQaFxtYQvnPG │         7.810 │
│ 8GpFJ8o6pVthTKmzimKxTTg8vT6sPFm44xz3nXNUMtbG │         4.197 │
│ 4mhTGao7SDTCsgZknLDhaboE9xBhkB56ZoWVyMzpA51E │        10.831 │
├──────────────────────────────────────────────┼───────────────┤
│      Found 5 offers with total rewards       │        45.186 │
╰──────────────────────────────────────────────┴───────────────╯
Claim all? [y/n]:
```

## Installing

It is recommended to install dexie-rewards using pip.

### Install via pip

```sh
pip install dexie-rewards
```
Note for macOS: If `pip` is not found, try `pip3` instead.

### Install from the repository (optional)

1. Clone the repository

```sh
git clone git@github.com:dexie-space/dexie-rewards.git
cd ./dexie-rewards/
```

2. Activate Poetry Shell

```sh
poetry shell
```

3. Install Dexie CLI

```sh
poetry install
```

## Configuration (optional)

In most cases the default configuration should be sufficient. However, if you want to use specific endpoints and paths, you can set the following environment variables:

```sh
export CHIA_ROOT="~/.chia/mainnet"
export DEXIE_URL="https://dexie.space"
export DEXIE_API_URL="https://api.dexie.space/v1/"
export DEXIE_DB_PATH="/dexie_db"
```

## Available Commands

Make sure that your Chia wallet is running and fully synced before using dexie-rewards. A full node is not required.

Run any command with the `--help` option to see all available functionality.

### List offers with outstanding (claimable) rewards
```
❯ dexie rewards list

  --fingerprint  -f        Set the fingerprint to specify which wallet to use
  --json         -j        Displays offers as JSON
  --verbose      -v        Display verbose output
  --help                   Show help and exit
```

### Claim all outstanding (claimable) rewards
```
❯ dexie rewards claim

  --fingerprint  -f         Set the fingerprint to specify which wallet to use
  --verify-only  -vo        Only verify the claim, don't actually claim
  --yes          -y         Skip claim confirmation
  --verbose      -v         Display verbose output
  --target       -t         Specify a target address to claim rewards to 
  --help                    Show help and exit
```

## Troubleshooting

If you encounter any issues, follow these steps to help identify and resolve them:

1. **Check your Python version**: Ensure you are using Python 3.11 or later, as older versions are not supported.

2. **Update packages**: Update both dexie-rewards and its dependencies by running `pip install --upgrade dexie-rewards`.

3. **Verify configuration**: Double-check the environment variables (if set) to ensure they are correct.

4. **Enable verbose output**: Use the `-v` or `--verbose` option with the relevant command to get more detailed output, which can help pinpoint the issue.

5. **Check for known issues**: Review the [issue tracker](https://github.com/dexie-space/dexie-rewards/issues) to see if the problem you are experiencing has been reported and if there is a potential solution or workaround.

6. **Report a new issue**: If you can't find a solution in the issue tracker, create a new issue, providing all relevant information and steps to reproduce the problem. This will help us to address the issue and improve the tool.

7. **Seek community support**: Visit the [dexie Discord community](https://discord.gg/3xUrkAxUmd) for assistance, as other users may have encountered similar issues and can share their solutions or workarounds.

## Alternatives

Advanced market makers may develop their own tools for claiming liquidity rewards. Refer to the [dexie API documentation](https://dexie.space/api) for information on how to claim rewards for offers using the API.

## Contributions

Contributions are welcome and encouraged. Please fork the repository and submit a pull request to the `main` branch. If you have any questions, feel free to reach out to us on [Discord](https://discord.gg/3xUrkAxUmd).
