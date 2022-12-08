# y2k-audit-2022-11

Economic audit for Y2K.

See [`audit/`](./audit/) for the full audit report.


## Replication

To check the results, clone the repo

```sh
git clone https://github.com/smolquants/y2k-audit-2022-11.git
```

Install dependencies with [`hatch`](https://github.com/pypa/hatch) and [`ape`](https://github.com/ApeWorX/ape)

```sh
hatch build
hatch shell
(y2k-audit-2022-11) $ ape plugins install .
```

Setup your environment with an [Alchemy](https://www.alchemy.com) key

```sh
export WEB3_ALCHEMY_PROJECT_ID=<YOUR_PROJECT_ID>
```

Then launch [`ape-notebook`](https://github.com/ApeWorX/ape-notebook)

```sh
(y2k-audit-2022-11) $ ape notebook
```

## Scripts

Scripts using mock tokens and pools rely on [`ape-hardhat`](https://github.com/ApeWorX/ape-hardhat)
mainnet-fork functionality. These verify results estimated in the notebooks.

To run, install hardhat locally in the repo:

```sh
npm install --save-dev hardhat
```

and compile the needed mock contracts

```sh
hatch shell
(y2k-audit-2022-11) $ ape compile --size
```

Then e.g. run the Curve manipulation script

```sh
(y2k-audit-2022-11) $ ape run curve_manipulation
```
