The figure below presents the development process with {{open_autonomy}}: from the idea of an off-chain service to its deployment in production. If you have completed the [quick start guide](./quick_start.md) you have already navigated through a significant part of this process.

<figure markdown>
![](../images/development_process.svg)
<figcaption>Overview of the development process with the Open Autonomy framework</figcaption>
</figure>

This is a summary of each step:

1. [Draft the service idea.](./draft_service_idea_and_define_fsm_specification.md#draft-the-service-idea) Any service that needs to execute its functionality in an autonomous, transparent and decentralized way is a good candidate. You can take a look at some [use cases](../get_started/use_cases.md) to get an idea of what you can build with {{open_autonomy}}.

2. [Define the FSM specification.](./draft_service_idea_and_define_fsm_specification.md#define-the-fsm-specification) Describe the service business logic as a [finite-state machine (FSM)](../key_concepts/fsm.md) in a language understood by the framework. This specification defines what are the states of the service, and how to transit from one to another.

3. [Code the {{fsm_app}} skill.](./code_fsm_app_skill.md) The actual business logic is encoded in the {{fsm_app}} that lives inside each agent. Coding the {{fsm_app}} involves scaffolding the "skeleton" of the classes, and complete the actual details of the actions executed in each state.

4. [Define the agent.](./define_agent.md) Define the components of the agent required to execute your service, including the newly created {{fsm_app}}. You can reuse already existing components publicly available on a remote registry.

5. [Define the service.](./define_service.md) This consists in defining the service configuration and declaring what agents constitute the service, together with a number of configuration parameters required.

6. [Publish and mint packages.](./publish_mint_packages.md) Those are required steps to make the service publicly available in the remote registry and secure it in the {{ autonolas_protocol }}.

7. [Deploy the service.](./deploy_service.md) You can deploy directly your service locally for testing purposes. To deploy a production service secured in the {{ autonolas_protocol }} you first need to bring the service to the _Deployed_ state in the protocol.

## Populate the local registry for the guides

To follow the next sections, you need to populate the local registry with a number of [packages shipped with the framework](../package_list.md). To do so, edit the local registry index file (`./packages/packages.json`) and ensure that it has the following `third_party` entries:

```json
{
    "dev": {
    },
    "third_party": {
        "service/valory/hello_world/0.1.0": "bafybeihl6j7ihkytk4t4ca2ffhctpzydwi6r4a354ubjasttuv2pw4oaci",
        "agent/valory/hello_world/0.1.0": "bafybeihtmp45mbfs5tyzrgxfoimh552on6dif42ifqidifait3ej2m5zvq",
        "connection/valory/abci/0.1.0": "bafybeiba4qrqp27533v7modv7mgbu7ucy5p5xncl3uqbhf3mprimt6jqpy",
        "connection/valory/http_client/0.23.0": "bafybeid5ffvg76ejjoese7brj5ji3lx66cu7p2ixfwflpo6rgofkypfd7y",
        "connection/valory/ipfs/0.1.0": "bafybeiamz23olgtow4wqf7zpsfnfzf7pxiognrxl2mhn5kvqutlwhgukxa",
        "connection/valory/ledger/0.19.0": "bafybeibdsjmy4w2eyilbqc7yzutopl65qpeyspxwz7mjvirr52twhjlf5y",
        "contract/valory/service_registry/0.1.0": "bafybeiflkhzdcjdjdgkwkz76al3rkgd3ugmjue7ukg54loaxm2ldh7laqm",
        "protocol/open_aea/signing/1.0.0": "bafybeig2d36zxy65vd7fwhs7scotuktydcarm74aprmrb5nioiymr3yixm",
        "protocol/valory/abci/0.1.0": "bafybeiatodhboj6a3p35x4f4b342lzk6ckxpud23awnqbxwjeon3k5y36u",
        "protocol/valory/acn/1.1.0": "bafybeic6h55ov5lrzbah6fate54c4u6spopcexxspw3abotbmffabfddeu",
        "protocol/valory/contract_api/1.0.0": "bafybeid247uig2ekykdumh7ewhp2cdq7rchaeqjj6e7urx35zfpdl5zrn4",
        "protocol/valory/http/1.0.0": "bafybeih4azmfwtamdbkhztkm4xitep3gx6tfdnoz6tvllmaqnhu3klejfa",
        "protocol/valory/ipfs/0.1.0": "bafybeifi2nri7sprmkez4rqzwb4lnu6peoy3bax5k6asf6k5ms7kmjpmkq",
        "protocol/valory/ledger_api/1.0.0": "bafybeihmqzcbj6t7vxz2aehd5726ofnzsfjs5cwlf42ro4tn6i34cbfrc4",
        "protocol/valory/tendermint/0.1.0": "bafybeigydrbfrlmr4f7shbtqx44kvmbg22im27mxdap2e3m5tkti6t445y",
        "skill/valory/abstract_abci/0.1.0": "bafybeiabbhwj6nw2rhgr3hwoeeebqfhctshcby6wiz23ufylle2exavb7q",
        "skill/valory/abstract_round_abci/0.1.0": "bafybeiafen5kchaqlrzy57yh5bm5t6cwyrlvucueh6mkmttffzxp6catti",
        "skill/valory/hello_world_abci/0.1.0": "bafybeiebittgfcz4idj633fkrvu6qle2ajekdjxpp7slggyur7vv7s7hrq",
        "connection/valory/p2p_libp2p_client/0.1.0": "bafybeic6ayusdwy4dks75njwk32ac7ur7salgllwf4fdc34ue5z2k5iz4q"
    }
}
```

Execute the following command after updating the `packages.json` file:

```bash
autonomy packages sync
```

The framework will fetch components from the remote registry into the local registry.

!!! tip "Do you already have an existing agent or service?"

    If you already have an existing agent (or if you want to create a service with the default `hello_world` agent), you can skip to [Step 5](./define_service.md).

    If you already have an existing service (or if you want to test the default `hello_world` service), you can skip to [Step 6](./publish_mint_packages.md) or [Step 7](./deploy_service.md).
