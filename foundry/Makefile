-include .env

deploy:
	@echo "Deploying PythoraEntropy.sol to Arbitrum Sepolia..."
	forge create src/PythoraEntropy.sol:PythoraEntropy \
		--private-key 0xasdfasdfasdf \
		--rpc-url $(ARBITRUM_SEPOLIA_RPC_URL) \
		--broadcast \
		--constructor-args 0x549Ebba8036Ab746611B4fFA1423eb0A4Df61440

verify:
	@echo "Verifying contract on Arbitrum Sepolia Etherscan..."
	forge verify-contract --chain-id 421614 \
		--constructor-args $$(cast abi-encode "constructor(address)" 0x549Ebba8036Ab746611B4fFA1423eb0A4Df61440) \
		--watch \
		$(PYTHORA_ENTROPY_CONTRACT_ADDRESS) \
		src/PythoraEntropy.sol:PythoraEntropy \
		--etherscan-api-key $(ARBITRUM_SEPOLIA_ETHERSCAN_API_KEY)
