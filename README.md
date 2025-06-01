# 🤖 Pythora

**Pythora** is a decentralized agent built using the [Autonolas](https://olas.network/) framework to fetch real-time price feeds from the [Pyth Network](https://pyth.network/) off-chain and update them on-chain.
Pyth Network provides real-time financial market data to smart contracts, as well as allows to request secure, verifiable random numbers using Pyth Entropy. 
This project is designed for the "price pusher" use case.

> Built at [ETHPrague 2025](https://ethglobal.com/events/prague)

---

## Table of Contents

- [🤖 Pythora](#-pythora)
  - [Table of Contents](#table-of-contents)
  - [🧠 What It Does](#-what-it-does)
  - [🛠️ Technologies Used](#️-technologies-used)
  - [Development Tools](#development-tools)
  - [🚀 Getting Started](#-getting-started)
    - [Installation and Setup for Development](#installation-and-setup-for-development)
  - [Commands](#commands)
    - [Formatting](#formatting)
    - [Linting](#linting)
    - [Testing](#testing)
    - [Locking](#locking)
    - [all](#all)
  - [Acknowledgements](#acknowledgements)
  - [License](#license)

---

## 🧠 What It Does

Pythora creates an **Olas Agent** that:
1. **Fetches price data** from Pyth’s off-chain Hermes API.
2. **Processes and verifies** the data to meet on-chain formatting requirements.
3. **Updates the data on-chain** using the `updatePriceFeeds` method.
4. **Automates the cycle**, ensuring decentralized and continuous price updates with no manual intervention.

---

## 🛠️ Technologies Used

| Technology       | Purpose                              |
|------------------|--------------------------------------|
| **Pyth Network**  | Provides high-fidelity price feeds |
| **Autonolas**      | Framework for building autonomous agents |
| **EVM blockchain** | On-chain price updates to be used in DeFi protocols |

---

## Development Tools

This project was initially scaffolded using [adev](https://github.com/8ball030/auto_dev), an awesome tool that helped me quickly generate the agent structure. It also allowed me to seamlessly convert a Mermaid diagram into a well-structured behavior flow — saving a ton of time and effort!

---

## 🚀 Getting Started

### Installation and Setup for Development

If you're looking to contribute or develop with `pythora`, get the source code and set up the environment:

```shell
git clone https://github.com/Dakavon/agent_pythora --recurse-submodules
cd agent_pythora 
make install
```

## Commands

Here are common commands you might need while working with the project:

### Formatting

```shell
make fmt
```

### Linting

```shell
make lint
```

### Testing

```shell
make test
```

### Locking

```shell
make hashes
```

### all

```shell
make all
```

---

## Acknowledgements
Big thanks to my friends who supported me during this hackathon. Their guidance and help navigating complex tools were invaluable. Shoutout to:

- [8ball030](https://github.com/8ball030)
- [Karrenbelt](https://github.com/Karrenbelt)

I couldn’t have done it without you!

---

## License

This project is licensed under the [Apache License 2.0](https://www.apache.org/licenses/LICENSE-2.0)

