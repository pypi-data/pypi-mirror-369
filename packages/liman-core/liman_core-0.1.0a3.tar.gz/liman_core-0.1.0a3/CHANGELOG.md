# Changelog

## [0.1.0-a3](https://github.com/gurobokum/liman/compare/liman_core_py-v0.1.0-a1...liman_core_py-v0.1.0-a3) (2025-08-15)


### ⚠ BREAKING CHANGES

* **liman_core:** rework NodeActor

### ✨ Features

* **liman_core:** add full_name for nodes ([24c6038](https://github.com/gurobokum/liman/commit/24c60387857b70d7d97e761ae186e88c7563d384))
* **liman_core:** add StateStorage design ([5c11ac6](https://github.com/gurobokum/liman/commit/5c11ac61e60147f349659362486cc285a315e16b))
* **liman_core:** design Plugins system ([ef8bda2](https://github.com/gurobokum/liman/commit/ef8bda21a429d9a6ca91a9aacd4bb3d5320dcea7))
* **liman_core:** implement ConditionalEvaluator ([36a3d46](https://github.com/gurobokum/liman/commit/36a3d46f41dde87ee6879290131a3d42fe7044bd))
* **liman_core:** implement Executor ([e2529be](https://github.com/gurobokum/liman/commit/e2529be1bf82238c17ad2e2b795ba70aa4c2000b))
* **liman_core:** implement NodeActor and Nodes states ([843cd62](https://github.com/gurobokum/liman/commit/843cd6207efb589d5f0ff0df775a31bd54ab6abb))
* **liman_core:** implement ServiceAccount ([1e0613f](https://github.com/gurobokum/liman/commit/1e0613f79ba51519466873802ae3b5394a36b06b))
* **liman_core:** provide implementation for ToolNode invoke/ainvoke ([3559731](https://github.com/gurobokum/liman/commit/355973168436d5890552be00130d4aa9870e76ef))
* **liman_core:** support debug logging ([5707a15](https://github.com/gurobokum/liman/commit/5707a155f1c58a874d17359390dd9204f1342263))
* **liman_core:** support object parameter type in ToolNode ([6af6f4a](https://github.com/gurobokum/liman/commit/6af6f4aec1c68c9ad316e39491728bbc52e0ddd6))
* **liman_core:** support pathlib.Path as yaml_path ([374c367](https://github.com/gurobokum/liman/commit/374c3671082dbf47fc5b3aef81d754acd2e83131))
* **liman_core:** support print_spec for whole registry ([41248ed](https://github.com/gurobokum/liman/commit/41248ed9e29f42d6a3ce340b980e2349b433762b))


### 🐛 Bug Fixes

* **liman_core:** add self.node on init in ToolNode ([bdc7d92](https://github.com/gurobokum/liman/commit/bdc7d92728c0335d39b354445843ef31d7fda91c))
* **liman_core:** fix getting field name from spec of the auth plugin ([f3bab6e](https://github.com/gurobokum/liman/commit/f3bab6efe00e709bcd70c63080636a70c8a592e2))


### 🛠 Code Refactoring

* **liman_core, liman_openapi:** drop dishka di ([6be80ab](https://github.com/gurobokum/liman/commit/6be80ab6cda1bd55d64ae17019334cb05b4daee1))
* **liman_core, liman_openapi:** move nodes into separated folder ([cdcdb9a](https://github.com/gurobokum/liman/commit/cdcdb9ae1e4a32ccbfd5152ae547a252ee452471))
* **liman_core:** change state to status in NodeActor ([dc2e5f2](https://github.com/gurobokum/liman/commit/dc2e5f273e835d4568093082388109ed315b940a))
* **liman_core:** create NodeOutput and Result types ([58022eb](https://github.com/gurobokum/liman/commit/58022ebe401537bf8473971b417e503accd40c7a))
* **liman_core:** drop sync methods ([9026a7d](https://github.com/gurobokum/liman/commit/9026a7d74101ca41113c5d672d396199beb42396))
* **liman_core:** extract Component from BaseNode ([5480cd9](https://github.com/gurobokum/liman/commit/5480cd92d1bea54542c649589762d0c36c52e998))
* **liman_core:** merge AsyncNodeActor with NodeActor into single class ([5d92555](https://github.com/gurobokum/liman/commit/5d92555fca813ec3ebecbde21002932961798380))
* **liman_core:** move auth to plugins ([f13a9c0](https://github.com/gurobokum/liman/commit/f13a9c02f58cadc987d45f3863594812b9554d80))
* **liman_core:** raise InvalidSpecError on loading failed yaml structure ([35fa897](https://github.com/gurobokum/liman/commit/35fa8972dd9a25824ac3e1957c36fd5f6151cea6))
* **liman_core:** remove executor ([d9fa66f](https://github.com/gurobokum/liman/commit/d9fa66f0e3e36460f7182a45d297aeec5e25df3a))
* **liman_core:** rework NodeActor ([770bb27](https://github.com/gurobokum/liman/commit/770bb27e6ce5156cf38fd5f79cd28e8602a016c4))
* **liman_core:** split node actors ([9f8a8da](https://github.com/gurobokum/liman/commit/9f8a8da3e75a036e1bced225343432dd68643926))


### 📚 Documentation

* add codecov badges for python code ([e2da9c4](https://github.com/gurobokum/liman/commit/e2da9c412bf58f6821cd5f1a0533a27f45e98f2f))
* **liman_core:** update README.md ([0add60b](https://github.com/gurobokum/liman/commit/0add60b5fd68404c85149d075c9099ea402a3e93))


### ♻️ Tests

* **liman_core:** fix tests ([3f1cc14](https://github.com/gurobokum/liman/commit/3f1cc148a42fb66f18dba895dcaacd5dac4b094b))

## [0.1.0-a1](https://github.com/gurobokum/liman/compare/liman_core_py-v0.1.0-a0...liman_core_py-v0.1.0-a1) (2025-08-03)


### 🐛 Bug Fixes

* **liman_core:** fix from_yaml_path ([cd172d4](https://github.com/gurobokum/liman/commit/cd172d45c0efcd253725df7a18dd878f5e8ec221))

## 0.1.0-a0 (2025-08-03)


### ✨ Features

* add basic llm_node ([83e8968](https://github.com/gurobokum/liman/commit/83e8968a16cf8941dd906eba53c70b8096e508de))
* add dishka ([83ed845](https://github.com/gurobokum/liman/commit/83ed8450ca58ebb082c552c544f0bb79a32232a9))
* add langchain and rich ([a255f97](https://github.com/gurobokum/liman/commit/a255f9731af86734acc257caf220ccc7588daf89))
* add LocalizedValue pydantic validator ([3a24632](https://github.com/gurobokum/liman/commit/3a24632e1be9e009b3961c68e4bc961fcd42d11e))
* add name for nodes ([11330c7](https://github.com/gurobokum/liman/commit/11330c70d28a6db16805d3e1f608cb69525614b9))
* add normalize_dict language function ([77dc060](https://github.com/gurobokum/liman/commit/77dc060538941b521bbef0ae32eb59454deebd72))
* add protobuf ([f861ba3](https://github.com/gurobokum/liman/commit/f861ba3133d70ddc2ce083427c5b955a4f736d8f))
* add registry ([1878c5d](https://github.com/gurobokum/liman/commit/1878c5db3bbba92c78bfe1199148cdb317ff35dc))
* add tool triggers and prompt to ToolNode spec ([8e0bb91](https://github.com/gurobokum/liman/commit/8e0bb91a62a2a0223be464b68caf1271aeadbcef))
* add ToolNode empty class ([fdfef3b](https://github.com/gurobokum/liman/commit/fdfef3bdb0df13b8e66bc98af0ce38511f5bdf62))
* **liman_core:** add add_tools for LLMNode ([e0379ad](https://github.com/gurobokum/liman/commit/e0379ad1f8ff097dab8b97a5834fc0f500985c65))
* **liman_core:** add flatten_dict function ([a713ffb](https://github.com/gurobokum/liman/commit/a713ffbed81fd95a677a9f6e87da8c054d53b6ad))
* **liman_core:** add invoke and ainvoke abstractmethods ([ee97569](https://github.com/gurobokum/liman/commit/ee975690db7da56e5779e175f2718bca25106ba6))
* **liman_core:** add liman_finops module ([07a198c](https://github.com/gurobokum/liman/commit/07a198c3a0b5aff36df40c89ba941d20d10f205d))
* **liman_core:** add Node ([2b05a3a](https://github.com/gurobokum/liman/commit/2b05a3aee8f78661ed4d7663551f0eeefc235ec5))
* **liman_core:** add NodeActor ([b2b882a](https://github.com/gurobokum/liman/commit/b2b882adb913aa5891bf0aa04696a7ca3f7ec31d))
* **liman_core:** add print_spec method for ToolNode ([b16271c](https://github.com/gurobokum/liman/commit/b16271cc370695aca06a1b4d5a9b60e76907237e))
* **liman_core:** add tool calls ([9ad717b](https://github.com/gurobokum/liman/commit/9ad717b543221eda5769b61286de20c50d50c244))
* **liman_core:** implement DSL for Edge when attribute ([1593a06](https://github.com/gurobokum/liman/commit/1593a06978aea2d7057342b05d0cb1fdff02a4e3))
* **liman_core:** implement generating tool node description ([88fe7a0](https://github.com/gurobokum/liman/commit/88fe7a0b5b64caad8c0f2127738e7e53907523f8))
* **liman_core:** implement generating tool_schema and llm_node invoke ([1a8f3cb](https://github.com/gurobokum/liman/commit/1a8f3cbfa00bb2f3e128070bed9add5a6ebcf4bd))
* **liman_core:** implement LLMNode compile ([007cae1](https://github.com/gurobokum/liman/commit/007cae17f35a5d5e7bf2a489a00084ca2639e5fb))


### 🐛 Bug Fixes

* fix typing ([2dad432](https://github.com/gurobokum/liman/commit/2dad4320369655741554a1e0ecc70b98137588da))
* **liman_core:** add covariance for inputs in node invoke ([5b9ed48](https://github.com/gurobokum/liman/commit/5b9ed483cad280488654ffa0a37d9c164f3a16e5))
* **liman_core:** fix python-3.10 errors ([2bf9b1f](https://github.com/gurobokum/liman/commit/2bf9b1f170682ddf49e582b052859acb3f7ee9b0))
* **liman_core:** fix tests pytest.raises ([6491652](https://github.com/gurobokum/liman/commit/64916521594a9bc7a48010c3c709dc4e22dc131b))


### 🛠 Code Refactoring

* create base parent node class ([74de339](https://github.com/gurobokum/liman/commit/74de33952f6175de6d8c45ec664c9f46dfe4c6cc))
* drop protobuf ([baf82d3](https://github.com/gurobokum/liman/commit/baf82d36c7fe936895eef3e2ab2aa3be541796bd))
* **liman_core:** add attribute access for errors ([f3b5a19](https://github.com/gurobokum/liman/commit/f3b5a1957eaef6a9ffe7b90c0f1f3bc980d53fda))
* **liman_core:** drop liman_finops auto configure_instrumentor ([6147f17](https://github.com/gurobokum/liman/commit/6147f172cb3096612acbb8ccaad2f84fb1541f7b))
* **liman_core:** generate proper tool jsonschema ([bb3a9e6](https://github.com/gurobokum/liman/commit/bb3a9e676f0c4f9f0f6d6428a7341673706f35b4))
* **liman_core:** redesign Node's api ([24b8703](https://github.com/gurobokum/liman/commit/24b87038c2cad69a455c193c9fd494017935b3e7))
* move llm_node to the separated package ([7e6bc22](https://github.com/gurobokum/liman/commit/7e6bc22cf7a850087e1ddf5b3cacb45822e0a69c))
* use normalize_dict in llm_node ([df920f1](https://github.com/gurobokum/liman/commit/df920f1a40b889829c351efff928cdba93d85d00))


### 📚 Documentation

* **liman_core:** update README.md ([85adb61](https://github.com/gurobokum/liman/commit/85adb61dd6f152f670f18b254fbb0f66dcfbb7ea))
* update README.md ([90048cb](https://github.com/gurobokum/liman/commit/90048cbb46bc1371776df9c4a36b9524e6abb7ca))


### ♻️ Tests

* **liman_core:** add tests for tool_node utils ([8323552](https://github.com/gurobokum/liman/commit/8323552ecf1f52418376e7ce48b49e0b07e43afb))
* **liman_core:** drop unnecessary dict ([2c1945a](https://github.com/gurobokum/liman/commit/2c1945a8ec5aafbd8d487b5d766772035eb2ff4a))
