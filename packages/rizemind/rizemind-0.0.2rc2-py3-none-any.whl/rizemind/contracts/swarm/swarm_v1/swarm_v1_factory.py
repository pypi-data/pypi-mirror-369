import os
from logging import INFO
from pathlib import Path
from typing import cast

from eth_account.signers.base import BaseAccount
from eth_account.types import TransactionDictType
from eth_typing import ChecksumAddress
from flwr.common.logger import log
from pydantic import BaseModel, Field
from rizemind.contracts.abi_helper import load_abi
from rizemind.contracts.deployment import DeployedContract
from rizemind.contracts.local_deployment import load_forge_artifact
from rizemind.web3.chains import RIZENET_TESTNET_CHAINID
from web3 import Web3


class SwarmV1FactoryConfig(BaseModel):
    name: str = Field(..., description="The swarm name")
    ticker: str | None = Field(None, description="The ticker symbol of the swarm")
    local_factory_deployment_path: str | None = Field(
        None, description="path to local deployments"
    )

    factory_deployments: dict[int, DeployedContract] = {
        RIZENET_TESTNET_CHAINID: DeployedContract(
            address=Web3.to_checksum_address(
                "0x6363a330D80E0Ed348FA203f31C5c1d2B7731e04"
            )
        )
    }

    def __init__(self, **data):
        super().__init__(**data)
        if self.ticker is None:
            self.ticker = self.name  # Default to name if ticker is not provided

    def get_factory_deployment(self, chain_id: int) -> DeployedContract:
        if self.local_factory_deployment_path is not None:
            return load_forge_artifact(
                Path(self.local_factory_deployment_path), "SwarmV1Factory"
            )
        if chain_id in self.factory_deployments:
            return self.factory_deployments[chain_id]
        raise Exception(
            f"Chain ID#{chain_id} is unsupported, provide a local_deployment_path"
        )


abi = load_abi(Path(os.path.dirname(__file__)) / "./factory_abi.json")


class SwarmV1Factory:
    config: SwarmV1FactoryConfig

    def __init__(self, config: SwarmV1FactoryConfig):
        self.config = config

    def deploy(
        self, deployer: BaseAccount, member_address: list[ChecksumAddress], w3: Web3
    ):
        factory_meta = self.config.get_factory_deployment(w3.eth.chain_id)
        factory = w3.eth.contract(abi=abi, address=factory_meta.address_as_bytes())
        log(INFO, "Web3 swarm contract address: %s", factory_meta.address)

        tx = factory.functions.createSwarm(
            self.config.name, self.config.ticker, deployer.address, member_address
        ).build_transaction(
            {
                "from": deployer.address,
                "nonce": w3.eth.get_transaction_count(deployer.address),
            }
        )

        signed_tx = deployer.sign_transaction(cast(TransactionDictType, tx))

        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)

        tx_receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        assert tx_receipt["status"] != 0, "Deployment transaction failed or reverted."

        logs = factory.events.ContractCreated().process_receipt(tx_receipt)
        assert len(logs) == 1, "no events discovered, factory might not be deployed"
        contract_created = logs[0]
        proxy_address = contract_created["args"]["proxyAddress"]

        return DeployedContract(address=proxy_address)
