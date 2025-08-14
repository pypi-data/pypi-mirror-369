# Changelog

## 2.8.0 (2025-08-13)

Full Changelog: [v2.7.0...v2.8.0](https://github.com/openintegrations/python-sdk/compare/v2.7.0...v2.8.0)

### Features

* **api:** exposing more APIs ([1dc7eb4](https://github.com/openintegrations/python-sdk/commit/1dc7eb455b99c94c4bb00c95c9e63d99ee1d11ea))
* **api:** new endpoints ([73c7b5d](https://github.com/openintegrations/python-sdk/commit/73c7b5d69f08d5dbbeb0e77a27c330e4dadc7307))
* clean up environment call outs ([0de7cb3](https://github.com/openintegrations/python-sdk/commit/0de7cb3fe67f104d2786e9353cecd9e46e574ea1))
* **client:** add follow_redirects request option ([b9b9a31](https://github.com/openintegrations/python-sdk/commit/b9b9a31b91ad89eaaae440a5c0e979b18cd80d9e))
* **client:** add support for aiohttp ([1f74a9a](https://github.com/openintegrations/python-sdk/commit/1f74a9a2c8ff4e8d92991f5d6d2a1b41eb0bef0e))
* **docs:** updating documented docs for stainless ([735f889](https://github.com/openintegrations/python-sdk/commit/735f88912419dbdc3a80d0b665bdcef84cc26427))
* **docs:** updating documented docs for stainless ([365ba48](https://github.com/openintegrations/python-sdk/commit/365ba486e77ce93e68a80a48649626119927b7b4))
* **docs:** updating documented docs for stainless ([4d50fa2](https://github.com/openintegrations/python-sdk/commit/4d50fa222eaac99eb9b71b01c192c002720852cf))


### Bug Fixes

* **ci:** correct conditional ([3c5fa29](https://github.com/openintegrations/python-sdk/commit/3c5fa29b84f0bfdf76f05b7adca4cf8374afe425))
* **ci:** release-doctor — report correct token name ([afdd5f4](https://github.com/openintegrations/python-sdk/commit/afdd5f492ce333fb11913b2c247b9af8292f1f24))
* **client:** correctly parse binary response | stream ([caa6b27](https://github.com/openintegrations/python-sdk/commit/caa6b273178dbed4a68f007498fdc1aa0bd806b1))
* **client:** don't send Content-Type header on GET requests ([c93f487](https://github.com/openintegrations/python-sdk/commit/c93f48787feef9bfadb7d4a4d740138cf9c5819b))
* **parsing:** correctly handle nested discriminated unions ([21690ae](https://github.com/openintegrations/python-sdk/commit/21690ae92ff4e64eee4ea06050630f221018a4fe))
* **parsing:** ignore empty metadata ([e261c8d](https://github.com/openintegrations/python-sdk/commit/e261c8d982826578cd2722dafa820c2c59928a33))
* **parsing:** parse extra field types ([ad534e6](https://github.com/openintegrations/python-sdk/commit/ad534e6e930a4d5151a3cfdb9418e90e3670a7ab))


### Chores

* **ci:** change upload type ([3617fa8](https://github.com/openintegrations/python-sdk/commit/3617fa8cb1ce2407e0368a4bde03a29380dc6163))
* **ci:** enable for pull requests ([931d7a6](https://github.com/openintegrations/python-sdk/commit/931d7a69639ed5e97247b25d7948830bd0f6722e))
* **ci:** only run for pushes and fork pull requests ([7dc816a](https://github.com/openintegrations/python-sdk/commit/7dc816a1047a7b076b85745aa9cea3074e8657ea))
* **docs:** remove reference to rye shell ([9a8cb2f](https://github.com/openintegrations/python-sdk/commit/9a8cb2f511a40dfdfbd2ab037505b15e95b2b5a4))
* **docs:** remove unnecessary param examples ([eeb75d3](https://github.com/openintegrations/python-sdk/commit/eeb75d3ba0620c94e84975c3963f751545c3e525))
* **internal:** bump pinned h11 dep ([30b9c6f](https://github.com/openintegrations/python-sdk/commit/30b9c6fd75dd3138d8018e27e8efedbc09757e3e))
* **internal:** codegen related update ([9bcaeb5](https://github.com/openintegrations/python-sdk/commit/9bcaeb5741a5deb86b7033e8038ba5b0a5239682))
* **internal:** update conftest.py ([c7fb0bb](https://github.com/openintegrations/python-sdk/commit/c7fb0bbc6dae0c4f04f6d71b9b247fdbd7c455fd))
* **package:** mark python 3.13 as supported ([7816ba8](https://github.com/openintegrations/python-sdk/commit/7816ba8cf4cc1b395b488a5b899eeee3a5c6e9ef))
* **project:** add settings file for vscode ([bd8d6a2](https://github.com/openintegrations/python-sdk/commit/bd8d6a28c1cf97bc10405bacb84703a01a562c64))
* **readme:** fix version rendering on pypi ([ff23de4](https://github.com/openintegrations/python-sdk/commit/ff23de4d954014004757e17fb5c016ca6a97a023))
* **readme:** update badges ([80e3c80](https://github.com/openintegrations/python-sdk/commit/80e3c8052559c503805acce6b9371fd8fa61e2f4))
* **tests:** add tests for httpx client instantiation & proxies ([fb80b72](https://github.com/openintegrations/python-sdk/commit/fb80b72788f99715598043f3f8fd807f207a6041))
* **tests:** run tests in parallel ([2944351](https://github.com/openintegrations/python-sdk/commit/2944351d65ce2c8a2499377f508b0ed3d32211ec))
* **tests:** skip some failing tests on the latest python versions ([a49ae20](https://github.com/openintegrations/python-sdk/commit/a49ae20e614483d37f8353da78c0c2c731287342))


### Documentation

* **client:** fix httpx.Timeout documentation reference ([defb222](https://github.com/openintegrations/python-sdk/commit/defb22221843470910685c6aef3ca0c5e0805db2))

## 2.7.0 (2025-05-30)

Full Changelog: [v2.6.0...v2.7.0](https://github.com/openintegrations/python-sdk/compare/v2.6.0...v2.7.0)

### Features

* **api:** coercing expand array ([e4a4abf](https://github.com/openintegrations/python-sdk/commit/e4a4abfec3d912271fc5ab5d0cb344b18020b98c))
* **docs:** updating documented docs for stainless ([370267f](https://github.com/openintegrations/python-sdk/commit/370267f29ab9eb07bc842ce9a977e161a8147ffe))

## 2.6.0 (2025-05-29)

Full Changelog: [v2.5.0...v2.6.0](https://github.com/openintegrations/python-sdk/compare/v2.5.0...v2.6.0)

### Features

* **docs:** updating documented docs for stainless ([dd0da8d](https://github.com/openintegrations/python-sdk/commit/dd0da8de0a3461bff861fb232374a5e065e091db))


### Bug Fixes

* **api:** adding prompt parameter ([f3e2286](https://github.com/openintegrations/python-sdk/commit/f3e2286b17393f506724721b5fbc0f6e05c4969e))

## 2.5.0 (2025-05-29)

Full Changelog: [v2.4.0...v2.5.0](https://github.com/openintegrations/python-sdk/compare/v2.4.0...v2.5.0)

### Features

* **docs:** updating documented docs for stainless ([92e2a7a](https://github.com/openintegrations/python-sdk/commit/92e2a7a1f7a04df1fe43319b95bbc97c4ce7a7a0))

## 2.4.0 (2025-05-29)

Full Changelog: [v2.3.0...v2.4.0](https://github.com/openintegrations/python-sdk/compare/v2.3.0...v2.4.0)

### Features

* **api:** add models ([4da6d66](https://github.com/openintegrations/python-sdk/commit/4da6d6652a088cd8833a25cdb6a3c326ef7b4e00))
* **api:** Adding models ([52c515e](https://github.com/openintegrations/python-sdk/commit/52c515e0e48e59d4c306a9a602b1bf6e371cdc22))
* **api:** updating oas ([6cdfe52](https://github.com/openintegrations/python-sdk/commit/6cdfe52906d50e482b0fe57ba28f1ca827350a7e))

## 2.3.0 (2025-05-28)

Full Changelog: [v2.2.0...v2.3.0](https://github.com/openintegrations/python-sdk/compare/v2.2.0...v2.3.0)

### Features

* **api:** adding listEvents ([876e541](https://github.com/openintegrations/python-sdk/commit/876e541830fb00fc015731600f7e9ca9f5e697e4))
* **api:** rename sdk name ([7cfd633](https://github.com/openintegrations/python-sdk/commit/7cfd6338a35478104fad4b9cb89bff4ad8fecdab))
* **docs:** updating documented docs for stainless ([c68d363](https://github.com/openintegrations/python-sdk/commit/c68d363f2fabd6d3bb3f9fab692cccd147deff20))


### Chores

* **docs:** grammar improvements ([bb4cb0a](https://github.com/openintegrations/python-sdk/commit/bb4cb0aceeee085eeeade60be737e88cb9cbeb23))

## 2.2.0 (2025-05-19)

Full Changelog: [v2.1.0...v2.2.0](https://github.com/openintegrations/python-sdk/compare/v2.1.0...v2.2.0)

### Features

* **docs:** updating documented docs for stainless ([df87cf1](https://github.com/openintegrations/python-sdk/commit/df87cf1bd25609ff6451e4c83cb2510e9b93aac4))

## 2.1.0 (2025-05-19)

Full Changelog: [v2.0.0...v2.1.0](https://github.com/openintegrations/python-sdk/compare/v2.0.0...v2.1.0)

### Features

* **api:** adding message template ([85b7294](https://github.com/openintegrations/python-sdk/commit/85b729443bfe6aed5b5e1335a058ea721a425ec8))
* **api:** scheme sync ([db2b3f4](https://github.com/openintegrations/python-sdk/commit/db2b3f4d82a2a498b4b67eadc5191a3e1ff28220))
* **docs:** updating documented docs for stainless ([b5af4c3](https://github.com/openintegrations/python-sdk/commit/b5af4c3102c40db19cac6fbac2968b2d453e2764))

## 2.0.0 (2025-05-19)

Full Changelog: [v1.6.1...v2.0.0](https://github.com/openintegrations/python-sdk/compare/v1.6.1...v2.0.0)

### ⚠ BREAKING CHANGES

* **api:** Updating sdk auth schem

### Features

* **api:** Updating sdk auth schem ([1097f03](https://github.com/openintegrations/python-sdk/commit/1097f03ca967070956a0211dcbf2e1f948fa17c1))

## 1.6.1 (2025-05-16)

Full Changelog: [v1.6.0...v1.6.1](https://github.com/openintegrations/python-sdk/compare/v1.6.0...v1.6.1)

### Bug Fixes

* **package:** support direct resource imports ([f5c4e06](https://github.com/openintegrations/python-sdk/commit/f5c4e06c3c0477290c15c0827727d47f058348ca))


### Chores

* **ci:** fix installation instructions ([da67dbd](https://github.com/openintegrations/python-sdk/commit/da67dbd9f87c61c0c2348764a0b6242644056b56))
* **ci:** upload sdks to package manager ([129ef64](https://github.com/openintegrations/python-sdk/commit/129ef6470c9fe83c70c3ca808fa40c0881854ba0))
* **internal:** avoid errors for isinstance checks on proxies ([9ee5f5e](https://github.com/openintegrations/python-sdk/commit/9ee5f5e1d27707d72f2493b0c1ea1670d04a2852))
* **internal:** avoid lint errors in pagination expressions ([8bac923](https://github.com/openintegrations/python-sdk/commit/8bac923acbe2aa243c01d6e066b171370e04cceb))
* remove custom code ([e353f63](https://github.com/openintegrations/python-sdk/commit/e353f63ea4a699a6980138facc41d7b7cfdf67ba))
* sync repo ([52ac08c](https://github.com/openintegrations/python-sdk/commit/52ac08c3179acfa776adbde54a3055786a0ba3ea))

## 1.5.0 (2025-04-23)

Full Changelog: [v1.4.0...v1.5.0](https://github.com/openintegrations/python-sdk/compare/v1.4.0...v1.5.0)

### Features

* **docs:** updating documented docs for stainless ([f18a77c](https://github.com/openintegrations/python-sdk/commit/f18a77c7f64f898cbdcd79a1f5fcf8b7a69d6633))
* **docs:** updating documented docs for stainless ([992c9f5](https://github.com/openintegrations/python-sdk/commit/992c9f503f31fd41c23ab91511bc04e662411652))
* **docs:** updating documented docs for stainless ([05e511c](https://github.com/openintegrations/python-sdk/commit/05e511cdc842d06146cf66e584a6bcbe6e2b00d8))
* **docs:** updating documented docs for stainless ([78b6e95](https://github.com/openintegrations/python-sdk/commit/78b6e9525a9bd78f16f8281ab9c2da7444f58749))
* **docs:** updating documented docs for stainless ([042cfc5](https://github.com/openintegrations/python-sdk/commit/042cfc52904e0432958b01414cc640c420d13244))


### Bug Fixes

* **pydantic v1:** more robust ModelField.annotation check ([d0ef0a7](https://github.com/openintegrations/python-sdk/commit/d0ef0a7c4ed1b4e6a40caa676389e43c880ca052))


### Chores

* **ci:** add timeout thresholds for CI jobs ([727c6e6](https://github.com/openintegrations/python-sdk/commit/727c6e67e6d49f595c770c193c22a9d39faa95ca))
* **internal:** fix list file params ([65529ca](https://github.com/openintegrations/python-sdk/commit/65529ca89d80ca4cf43f17be158afa7c138ab37c))
* **internal:** refactor retries to not use recursion ([3b25e8d](https://github.com/openintegrations/python-sdk/commit/3b25e8d4a304edcb193a2d5dc7ccce0e043bad47))
* **internal:** update models test ([5b1658c](https://github.com/openintegrations/python-sdk/commit/5b1658c4b014410e16ec558c955d0435a7244cf9))

## 1.4.0 (2025-04-17)

Full Changelog: [v1.3.0...v1.4.0](https://github.com/openintegrations/python-sdk/compare/v1.3.0...v1.4.0)

### Features

* **docs:** updating documented docs for stainless ([#59](https://github.com/openintegrations/python-sdk/issues/59)) ([67d2b1a](https://github.com/openintegrations/python-sdk/commit/67d2b1afd93f7c03ec0cf4b9efca10955e67b0a2))
* **docs:** updating documented docs for stainless ([#60](https://github.com/openintegrations/python-sdk/issues/60)) ([3198217](https://github.com/openintegrations/python-sdk/commit/3198217a87b4905bccd2a2aa8b73d1d7078c64dd))
* **docs:** updating documented docs for stainless ([#63](https://github.com/openintegrations/python-sdk/issues/63)) ([c58d10f](https://github.com/openintegrations/python-sdk/commit/c58d10f974edc4e5b0a4b773e491ac15dc0a6a1a))


### Bug Fixes

* **api:** adding list connectors ([#57](https://github.com/openintegrations/python-sdk/issues/57)) ([4346d9f](https://github.com/openintegrations/python-sdk/commit/4346d9f25c93a12cc9d053a875f7ddd8713ad8b2))
* **client:** add missing `None` default ([#62](https://github.com/openintegrations/python-sdk/issues/62)) ([c485bed](https://github.com/openintegrations/python-sdk/commit/c485bed766abe22f064cbe35e565dd46a7c65153))
* **client:** send all configured auth headers ([#64](https://github.com/openintegrations/python-sdk/issues/64)) ([d275e08](https://github.com/openintegrations/python-sdk/commit/d275e08a1ad94ceb314199a05ac77f4fe3fa42c5))
* **perf:** optimize some hot paths ([0cfd3e8](https://github.com/openintegrations/python-sdk/commit/0cfd3e84986aab3170fe95d03914fca2cf4a6de1))
* **perf:** skip traversing types for NotGiven values ([8701b67](https://github.com/openintegrations/python-sdk/commit/8701b673ba7330a950b8b01ced03e7f932aafc1c))


### Chores

* **client:** minor internal fixes ([51521a0](https://github.com/openintegrations/python-sdk/commit/51521a02d06ba4735c88b2a2c4a8e5cbc1a73fc4))
* **internal:** base client updates ([b363862](https://github.com/openintegrations/python-sdk/commit/b363862cbc085488312f80981f866bf116e49b42))
* **internal:** bump pyright version ([218ab17](https://github.com/openintegrations/python-sdk/commit/218ab17be07865cca836d851809edf2e1aa11943))
* **internal:** expand CI branch coverage ([2fd500b](https://github.com/openintegrations/python-sdk/commit/2fd500bff96581dad3331a0a89e2a02d0a00f872))
* **internal:** reduce CI branch coverage ([763f501](https://github.com/openintegrations/python-sdk/commit/763f501a41880cfff017f4469863d0d5e2e3789d))
* **internal:** remove trailing character ([#61](https://github.com/openintegrations/python-sdk/issues/61)) ([b5d7c1c](https://github.com/openintegrations/python-sdk/commit/b5d7c1ca8c2180df9c831996e0253415e0b0571b))
* **internal:** slight transform perf improvement ([#65](https://github.com/openintegrations/python-sdk/issues/65)) ([8ec7112](https://github.com/openintegrations/python-sdk/commit/8ec71120f3f140b0998e561bb738b7de6bb0c489))
* **internal:** update pyright settings ([075ff3f](https://github.com/openintegrations/python-sdk/commit/075ff3f61e5dcfc11e68df7db663e5611f1c064a))

## 1.3.0 (2025-04-03)

Full Changelog: [v1.2.0...v1.3.0](https://github.com/openintegrations/python-sdk/compare/v1.2.0...v1.3.0)

### Features

* **docs:** updating documented docs for stainless ([#54](https://github.com/openintegrations/python-sdk/issues/54)) ([246ab15](https://github.com/openintegrations/python-sdk/commit/246ab159d469fb878f55f23d1df30605f5c2dbec))

## 1.2.0 (2025-04-02)

Full Changelog: [v1.1.0...v1.2.0](https://github.com/openintegrations/python-sdk/compare/v1.1.0...v1.2.0)

### Features

* **docs:** updating documented docs for stainless ([#51](https://github.com/openintegrations/python-sdk/issues/51)) ([bd825cf](https://github.com/openintegrations/python-sdk/commit/bd825cf2d45569599927a6cd7cb4f70f8c56df50))

## 1.1.0 (2025-04-02)

Full Changelog: [v1.0.0...v1.1.0](https://github.com/openintegrations/python-sdk/compare/v1.0.0...v1.1.0)

### Features

* **api:** Reverting name update ([#49](https://github.com/openintegrations/python-sdk/issues/49)) ([45042ce](https://github.com/openintegrations/python-sdk/commit/45042ce8f3da602d96fdbef99318e353374fc98e))
* **api:** Updating Name ([#47](https://github.com/openintegrations/python-sdk/issues/47)) ([8cd1dc1](https://github.com/openintegrations/python-sdk/commit/8cd1dc1d841abd0c0685626d0c3d621064e80df4))

## 1.0.0 (2025-04-02)

Full Changelog: [v0.1.0-alpha.5...v1.0.0](https://github.com/openintegrations/python-sdk/compare/v0.1.0-alpha.5...v1.0.0)

### Features

* **api:** fix delete ([#45](https://github.com/openintegrations/python-sdk/issues/45)) ([9a774ff](https://github.com/openintegrations/python-sdk/commit/9a774ff69ef220b1eca5111ee96583f2616c86d7))


### Chores

* remove custom code ([0f8c34c](https://github.com/openintegrations/python-sdk/commit/0f8c34cebf0ded97645adcf3cf65bc742c5bf897))

## 0.1.0-alpha.5 (2025-03-17)

Full Changelog: [v0.1.0-alpha.4...v0.1.0-alpha.5](https://github.com/openintegrations/python-sdk/compare/v0.1.0-alpha.4...v0.1.0-alpha.5)

### Features

* **api:** Adding viewer endpoint ([#21](https://github.com/openintegrations/python-sdk/issues/21)) ([94978b8](https://github.com/openintegrations/python-sdk/commit/94978b8912be1b7aa481c1a256e2253064c34183))
* **api:** Fixing api key auth ([#22](https://github.com/openintegrations/python-sdk/issues/22)) ([9ab6603](https://github.com/openintegrations/python-sdk/commit/9ab66033155b216c94ed2e72a3fbadce6a5f1982))
* **api:** manual updates ([902c691](https://github.com/openintegrations/python-sdk/commit/902c691f121e2776b1201d00e19a162cc1042068))
* **api:** manual updates ([31a2107](https://github.com/openintegrations/python-sdk/commit/31a210705217385bd71aa4b9457b150cc344ea26))
* **api:** manual updates ([1bc0aa4](https://github.com/openintegrations/python-sdk/commit/1bc0aa4d20fe0b771dfd0861db85144b2c482dfe))
* **api:** manual updates ([735882e](https://github.com/openintegrations/python-sdk/commit/735882e65872becb2622e4b7d41faf610bdcaa73))
* **api:** manual updates ([#10](https://github.com/openintegrations/python-sdk/issues/10)) ([ee8775b](https://github.com/openintegrations/python-sdk/commit/ee8775bcbe538e4ee176ea6b70613f0e7118627f))
* **api:** manual updates ([#11](https://github.com/openintegrations/python-sdk/issues/11)) ([035fbea](https://github.com/openintegrations/python-sdk/commit/035fbead3a022304829924c9996f434a7cd4a593))
* **api:** manual updates ([#12](https://github.com/openintegrations/python-sdk/issues/12)) ([6dfc2e8](https://github.com/openintegrations/python-sdk/commit/6dfc2e881d3b6b113a597c2a9251a00c3203ce84))
* **api:** manual updates ([#13](https://github.com/openintegrations/python-sdk/issues/13)) ([224a7a0](https://github.com/openintegrations/python-sdk/commit/224a7a02297b3b06218ae5f8297c1e829cb91037))
* **api:** manual updates ([#15](https://github.com/openintegrations/python-sdk/issues/15)) ([199f161](https://github.com/openintegrations/python-sdk/commit/199f1610fbc61365c5a4184155b5c99bd72bc116))
* **api:** manual updates ([#17](https://github.com/openintegrations/python-sdk/issues/17)) ([280560d](https://github.com/openintegrations/python-sdk/commit/280560daa08c6650e3f328eddca4352502b956d2))
* **api:** manual updates ([#18](https://github.com/openintegrations/python-sdk/issues/18)) ([524d083](https://github.com/openintegrations/python-sdk/commit/524d083ae36025ce93b4b33ac33d2074d7efae74))
* **api:** manual updates ([#20](https://github.com/openintegrations/python-sdk/issues/20)) ([375e0a4](https://github.com/openintegrations/python-sdk/commit/375e0a47770a2d1b39407c22f3f4bda815ee12cd))
* **api:** manual updates ([#7](https://github.com/openintegrations/python-sdk/issues/7)) ([6b05d11](https://github.com/openintegrations/python-sdk/commit/6b05d115709fed32c7c6884621ac0959abf75ea1))
* **api:** manual updates ([#8](https://github.com/openintegrations/python-sdk/issues/8)) ([5054460](https://github.com/openintegrations/python-sdk/commit/5054460f4d5e441afd71fe29a1ab3ef11ec82cba))
* **api:** manual updates ([#9](https://github.com/openintegrations/python-sdk/issues/9)) ([ac996eb](https://github.com/openintegrations/python-sdk/commit/ac996ebde3816be7fcef375087d13d62d85374f0))
* **api:** Updating viewer enum ([#23](https://github.com/openintegrations/python-sdk/issues/23)) ([4365bf7](https://github.com/openintegrations/python-sdk/commit/4365bf779458b6ac89af2b665ed1d46072a9cf7b))
* **docs:** updating documented docs for mintlify ([e757a5c](https://github.com/openintegrations/python-sdk/commit/e757a5cf1c3fc58a0eeccab66115c1bed18eaedc))
* **docs:** updating documented docs for mintlify ([84bb147](https://github.com/openintegrations/python-sdk/commit/84bb147ab12a84d308242735e5996d2c1b15ff1d))
* **docs:** updating documented docs for mintlify ([3ab7ade](https://github.com/openintegrations/python-sdk/commit/3ab7ade9e3d0e5c699ae5076e7695d1968768b57))
* **docs:** updating documented docs for mintlify ([#19](https://github.com/openintegrations/python-sdk/issues/19)) ([a6f4aae](https://github.com/openintegrations/python-sdk/commit/a6f4aaee848d37d7b1f82d5ba6738db8ee4ca420))
* **docs:** updating documented docs for mintlify ([#24](https://github.com/openintegrations/python-sdk/issues/24)) ([75a1fcd](https://github.com/openintegrations/python-sdk/commit/75a1fcde743331a0a788aa16992f13ecba2c7365))
* **docs:** updating documented docs for mintlify ([#5](https://github.com/openintegrations/python-sdk/issues/5)) ([80624c2](https://github.com/openintegrations/python-sdk/commit/80624c2bfe3e06d971af96da9a629123b7920290))
* **docs:** updating documented docs for stainless ([#26](https://github.com/openintegrations/python-sdk/issues/26)) ([ee7e8f9](https://github.com/openintegrations/python-sdk/commit/ee7e8f91e5ba13b06e959d9f5745ec691aa5987a))
* **docs:** updating documented docs for stainless ([#29](https://github.com/openintegrations/python-sdk/issues/29)) ([749df66](https://github.com/openintegrations/python-sdk/commit/749df664aaaacda0de8b781fdcd4d7e379e2ae5d))


### Bug Fixes

* **ci:** ensure pip is always available ([#36](https://github.com/openintegrations/python-sdk/issues/36)) ([52c3694](https://github.com/openintegrations/python-sdk/commit/52c36947734ae23c2a5dcc6da9bf771a184a1ae6))
* **types:** handle more discriminated union shapes ([#35](https://github.com/openintegrations/python-sdk/issues/35)) ([1c5878e](https://github.com/openintegrations/python-sdk/commit/1c5878e5c33c595a0307eae443bea025bb7c9fdd))


### Chores

* configure new SDK language ([8c5b8c0](https://github.com/openintegrations/python-sdk/commit/8c5b8c098e02ffcec4af1c39b314a9177d3ca8dd))
* configure new SDK language ([33af5c1](https://github.com/openintegrations/python-sdk/commit/33af5c174cae2c72e3460267cd7f0221e94a7f9d))
* go live ([#1](https://github.com/openintegrations/python-sdk/issues/1)) ([23281f8](https://github.com/openintegrations/python-sdk/commit/23281f821c95e8c4ca40f030916a0ced6c59092d))
* **internal:** bump rye to 0.44.0 ([#34](https://github.com/openintegrations/python-sdk/issues/34)) ([570fe3a](https://github.com/openintegrations/python-sdk/commit/570fe3a9323e5c9f51306e82e4ccbde02fc86aaa))
* **internal:** codegen related update ([df6dad6](https://github.com/openintegrations/python-sdk/commit/df6dad620d6dc210a73d81998f090832babc06db))
* **internal:** codegen related update ([2d08063](https://github.com/openintegrations/python-sdk/commit/2d0806324412bb8c471c20c3ad93204326335388))
* **internal:** codegen related update ([#32](https://github.com/openintegrations/python-sdk/issues/32)) ([efb587f](https://github.com/openintegrations/python-sdk/commit/efb587f600fca2c05d8edb4a792d9baabcc07ec4))
* **internal:** remove extra empty newlines ([#30](https://github.com/openintegrations/python-sdk/issues/30)) ([5d7bfbb](https://github.com/openintegrations/python-sdk/commit/5d7bfbb11557c7e1ca3e1e45fe105f565f6a041b))
* **internal:** remove unused http client options forwarding ([5e063e4](https://github.com/openintegrations/python-sdk/commit/5e063e41489414b8843879903f0ccf07e1fa2e7e))
* update SDK settings ([8018ccc](https://github.com/openintegrations/python-sdk/commit/8018ccc608e80e5b690f2962dace74de825908e6))
* update SDK settings ([#3](https://github.com/openintegrations/python-sdk/issues/3)) ([f14e8ec](https://github.com/openintegrations/python-sdk/commit/f14e8ec758033ba00469865d7e1387ceb7953473))

## 0.1.0-alpha.4 (2025-03-14)

Full Changelog: [v0.1.0-alpha.3...v0.1.0-alpha.4](https://github.com/openintegrations/python-sdk/compare/v0.1.0-alpha.3...v0.1.0-alpha.4)

### Features

* **docs:** updating documented docs for stainless ([#26](https://github.com/openintegrations/python-sdk/issues/26)) ([ee7e8f9](https://github.com/openintegrations/python-sdk/commit/ee7e8f91e5ba13b06e959d9f5745ec691aa5987a))
* **docs:** updating documented docs for stainless ([#29](https://github.com/openintegrations/python-sdk/issues/29)) ([749df66](https://github.com/openintegrations/python-sdk/commit/749df664aaaacda0de8b781fdcd4d7e379e2ae5d))


### Chores

* **internal:** remove extra empty newlines ([#30](https://github.com/openintegrations/python-sdk/issues/30)) ([5d7bfbb](https://github.com/openintegrations/python-sdk/commit/5d7bfbb11557c7e1ca3e1e45fe105f565f6a041b))

## 0.1.0-alpha.3 (2025-03-08)

Full Changelog: [v0.1.0-alpha.2...v0.1.0-alpha.3](https://github.com/openintegrations/python-sdk/compare/v0.1.0-alpha.2...v0.1.0-alpha.3)

### Features

* **api:** Adding viewer endpoint ([#21](https://github.com/openintegrations/python-sdk/issues/21)) ([94978b8](https://github.com/openintegrations/python-sdk/commit/94978b8912be1b7aa481c1a256e2253064c34183))
* **api:** Fixing api key auth ([#22](https://github.com/openintegrations/python-sdk/issues/22)) ([9ab6603](https://github.com/openintegrations/python-sdk/commit/9ab66033155b216c94ed2e72a3fbadce6a5f1982))
* **api:** manual updates ([#15](https://github.com/openintegrations/python-sdk/issues/15)) ([199f161](https://github.com/openintegrations/python-sdk/commit/199f1610fbc61365c5a4184155b5c99bd72bc116))
* **api:** manual updates ([#17](https://github.com/openintegrations/python-sdk/issues/17)) ([280560d](https://github.com/openintegrations/python-sdk/commit/280560daa08c6650e3f328eddca4352502b956d2))
* **api:** manual updates ([#18](https://github.com/openintegrations/python-sdk/issues/18)) ([524d083](https://github.com/openintegrations/python-sdk/commit/524d083ae36025ce93b4b33ac33d2074d7efae74))
* **api:** manual updates ([#20](https://github.com/openintegrations/python-sdk/issues/20)) ([375e0a4](https://github.com/openintegrations/python-sdk/commit/375e0a47770a2d1b39407c22f3f4bda815ee12cd))
* **api:** Updating viewer enum ([#23](https://github.com/openintegrations/python-sdk/issues/23)) ([4365bf7](https://github.com/openintegrations/python-sdk/commit/4365bf779458b6ac89af2b665ed1d46072a9cf7b))
* **docs:** updating documented docs for mintlify ([#19](https://github.com/openintegrations/python-sdk/issues/19)) ([a6f4aae](https://github.com/openintegrations/python-sdk/commit/a6f4aaee848d37d7b1f82d5ba6738db8ee4ca420))
* **docs:** updating documented docs for mintlify ([#24](https://github.com/openintegrations/python-sdk/issues/24)) ([75a1fcd](https://github.com/openintegrations/python-sdk/commit/75a1fcde743331a0a788aa16992f13ecba2c7365))

## 0.1.0-alpha.2 (2025-03-05)

Full Changelog: [v0.1.0-alpha.1...v0.1.0-alpha.2](https://github.com/openintegrations/python-sdk/compare/v0.1.0-alpha.1...v0.1.0-alpha.2)

### Features

* **api:** manual updates ([#10](https://github.com/openintegrations/python-sdk/issues/10)) ([ee8775b](https://github.com/openintegrations/python-sdk/commit/ee8775bcbe538e4ee176ea6b70613f0e7118627f))
* **api:** manual updates ([#11](https://github.com/openintegrations/python-sdk/issues/11)) ([035fbea](https://github.com/openintegrations/python-sdk/commit/035fbead3a022304829924c9996f434a7cd4a593))
* **api:** manual updates ([#12](https://github.com/openintegrations/python-sdk/issues/12)) ([6dfc2e8](https://github.com/openintegrations/python-sdk/commit/6dfc2e881d3b6b113a597c2a9251a00c3203ce84))
* **api:** manual updates ([#13](https://github.com/openintegrations/python-sdk/issues/13)) ([224a7a0](https://github.com/openintegrations/python-sdk/commit/224a7a02297b3b06218ae5f8297c1e829cb91037))
* **api:** manual updates ([#7](https://github.com/openintegrations/python-sdk/issues/7)) ([6b05d11](https://github.com/openintegrations/python-sdk/commit/6b05d115709fed32c7c6884621ac0959abf75ea1))
* **api:** manual updates ([#8](https://github.com/openintegrations/python-sdk/issues/8)) ([5054460](https://github.com/openintegrations/python-sdk/commit/5054460f4d5e441afd71fe29a1ab3ef11ec82cba))
* **api:** manual updates ([#9](https://github.com/openintegrations/python-sdk/issues/9)) ([ac996eb](https://github.com/openintegrations/python-sdk/commit/ac996ebde3816be7fcef375087d13d62d85374f0))
* **docs:** updating documented docs for mintlify ([#5](https://github.com/openintegrations/python-sdk/issues/5)) ([80624c2](https://github.com/openintegrations/python-sdk/commit/80624c2bfe3e06d971af96da9a629123b7920290))

## 0.1.0-alpha.1 (2025-03-04)

Full Changelog: [v0.0.1-alpha.0...v0.1.0-alpha.1](https://github.com/openintegrations/python-sdk/compare/v0.0.1-alpha.0...v0.1.0-alpha.1)

### Features

* **api:** manual updates ([902c691](https://github.com/openintegrations/python-sdk/commit/902c691f121e2776b1201d00e19a162cc1042068))
* **api:** manual updates ([31a2107](https://github.com/openintegrations/python-sdk/commit/31a210705217385bd71aa4b9457b150cc344ea26))
* **api:** manual updates ([1bc0aa4](https://github.com/openintegrations/python-sdk/commit/1bc0aa4d20fe0b771dfd0861db85144b2c482dfe))
* **api:** manual updates ([735882e](https://github.com/openintegrations/python-sdk/commit/735882e65872becb2622e4b7d41faf610bdcaa73))
* **docs:** updating documented docs for mintlify ([e757a5c](https://github.com/openintegrations/python-sdk/commit/e757a5cf1c3fc58a0eeccab66115c1bed18eaedc))
* **docs:** updating documented docs for mintlify ([84bb147](https://github.com/openintegrations/python-sdk/commit/84bb147ab12a84d308242735e5996d2c1b15ff1d))
* **docs:** updating documented docs for mintlify ([3ab7ade](https://github.com/openintegrations/python-sdk/commit/3ab7ade9e3d0e5c699ae5076e7695d1968768b57))


### Chores

* configure new SDK language ([8c5b8c0](https://github.com/openintegrations/python-sdk/commit/8c5b8c098e02ffcec4af1c39b314a9177d3ca8dd))
* configure new SDK language ([33af5c1](https://github.com/openintegrations/python-sdk/commit/33af5c174cae2c72e3460267cd7f0221e94a7f9d))
* go live ([#1](https://github.com/openintegrations/python-sdk/issues/1)) ([23281f8](https://github.com/openintegrations/python-sdk/commit/23281f821c95e8c4ca40f030916a0ced6c59092d))
* **internal:** codegen related update ([df6dad6](https://github.com/openintegrations/python-sdk/commit/df6dad620d6dc210a73d81998f090832babc06db))
* **internal:** codegen related update ([2d08063](https://github.com/openintegrations/python-sdk/commit/2d0806324412bb8c471c20c3ad93204326335388))
* **internal:** remove unused http client options forwarding ([5e063e4](https://github.com/openintegrations/python-sdk/commit/5e063e41489414b8843879903f0ccf07e1fa2e7e))
* update SDK settings ([8018ccc](https://github.com/openintegrations/python-sdk/commit/8018ccc608e80e5b690f2962dace74de825908e6))
* update SDK settings ([#3](https://github.com/openintegrations/python-sdk/issues/3)) ([f14e8ec](https://github.com/openintegrations/python-sdk/commit/f14e8ec758033ba00469865d7e1387ceb7953473))
