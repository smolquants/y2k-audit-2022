# y2k-audit-2022-11

Economic audit for Y2K

## Replication

To check the results, clone the repo

```sh
git clone https://github.com/smolquants/y2k-audit-2022-11.git
```

Install dependencies with [`hatch`](https://github.com/pypa/hatch) and [`ape`](https://github.com/ApeWorX/ape)

```sh
hatch build
hatch run ape plugins install .
```

Setup your environment with an [Alchemy](https://www.alchemy.com) key

```sh
export WEB3_ALCHEMY_PROJECT_ID=<YOUR_PROJECT_ID>
```

Then launch [`ape-notebook`](https://github.com/ApeWorX/ape-notebook)

```sh
hatch run ape notebook
```

## Scripts

The scripts to verify results from notebooks using mock tokens
and pools rely on the [`ape-hardhat`](https://github.com/ApeWorX/ape-hardhat)
mainnet-fork functionality.

To run the scripts, install hardhat locally in the repo:

```sh
npm install --save-dev hardhat
```

and compile the needed mock contracts

```sh
hatch run ape compile --size
```
