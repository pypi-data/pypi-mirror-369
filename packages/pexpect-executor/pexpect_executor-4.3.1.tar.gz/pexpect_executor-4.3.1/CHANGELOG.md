# Changelog

<a name="4.3.1"></a>
## [4.3.1](https://gitlab.com/RadianDevCore/tools/pexpect-executor/compare/4.3.0...4.3.1) (2025-08-13)

### ✨ Features

- **setup:** add support for Python 3.13 ([c856991](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/c8569916020d13a4965a045b46376f4144485422))

### 🐛 Bug Fixes

- **version:** migrate from deprecated 'pkg_resources' to 'packaging' ([a50de14](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/a50de1478d4fb468d082cc7ed00f1a7656ebe3b8))
- **version:** try getting version from bundle name too ([84d2b41](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/84d2b41c3f4c3953c8b00fd454b8da1f76b8fa2d))

### 📚 Documentation

- **docs:** use '<span class=page-break>' instead of '<div>' ([a6b1ece](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/a6b1ece75ed2977d0353917498119a268e0d88e7))
- **license, mkdocs:** raise copyright year to '2025' ([beec296](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/beec296f87f353717ab3077392ddeacbc5ead447))
- **mkdocs:** embed coverage HTML page with 'mkdocs-coverage' ([cd79967](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/cd799673373527898fcc2682e7804fdd4f41eb2e))
- **prepare:** avoid 'TOC' injection if 'hide:  - toc' is used ([1b4d454](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/1b4d454abac5e355e7b98ed347aad99c3e85f6c0))
- **prepare:** prepare empty HTML coverage report if missing locally ([4482176](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/448217634c8fd9cf5909764b38997abc59697b4f))
- **readme:** document 'mkdocs-coverage' plugin in references ([3355451](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/3355451d6d7ee947efe1cd967cb547e277d56e1d))

### 🎨 Styling

- **colors:** ignore 'Colored' import 'Incompatible import' warning ([9cfb2e3](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/9cfb2e33c707175f09c054b589eb85ca30583fdd))

### 🧪 Test

- **engines:** improve coverage results per Linux / Windows targets ([5f1c45c](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/5f1c45cf49a4ce5fef1abfd417e068db44a0e204))
- **platform:** improve coverage for Windows target ([512df66](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/512df6636b0c02c43217bb8771e13b73fe22a5a5))
- **versions:** ignore 'echo Test' attempts on Windows environments ([0035c00](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/0035c004c4764c9c087e88bd482636091fb253cb))

### ⚙️ Cleanups

- **gitlab-ci, docs, src:** resolve non breakable spacing chars ([e718242](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/e7182428284ecb33932f888852701effa2149d90))
- **pre-commit:** update against 'pre-commit-crocodile' 4.2.1 ([59959a1](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/59959a1b4256e09964c3574c484ffce90ec4fb54))
- **pre-commit:** migrate to 'pre-commit-crocodile' 5.0.0 ([49ab96a](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/49ab96add015a2de1160b05717d25c5c903961b7))
- **pre-commit:** migrate to 'pre-commit-crocodile' 6.1.0 ([8b27e2e](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/8b27e2ee3f5aa53c36b85c154bc0a2ec14d80862))
- **sonar-project:** configure coverage checks in SonarCloud ([a2e8b66](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/a2e8b6686786b535d790a7a067dae6077bfcbc08))
- **strings:** remove unused 'random' method and dependencies ([5d3c06e](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/5d3c06e73efa423f941e23da2acf646f1c85ff61))
- **vscode:** install 'ryanluker.vscode-coverage-gutters' ([3a5a551](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/3a5a5513b86b61262f7054c88f4cec513f1fb259))
- **vscode:** configure coverage file and settings ([3f1be50](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/3f1be506106f32e44f1f8647675eea4d2689e689))

### 🚀 CI

- **coveragerc, gitlab-ci:** implement coverage specific exclusions ([b3f23d6](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/b3f23d69357e23e8bb00fec722727a3c8d399311))
- **gitlab-ci:** run coverage jobs if 'sonar-project.properties' changes ([baade22](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/baade22ef009bc449f71c771c9488a1de7d91a3a))
- **gitlab-ci:** watch for 'docs/.*' changes in 'pages' jobs ([d17823e](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/d17823e7ca87a66a0848a19c3e8e7a79f2a3f001))
- **gitlab-ci:** migrate to 'pre-commit-crocodile/commits@4.1.0' ([7225677](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/7225677d7851b2a5c5cbcce09b26f7f99bed5d6b))
- **gitlab-ci:** remove unrequired 'stage: deploy' in 'pdf' job ([74f7392](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/74f7392a743842aaad8950ff6c27c9bcf6f1831a))
- **gitlab-ci:** improve combined coverage local outputs ([5edc21e](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/5edc21ee238156ccb9ae293fde43691531e476f2))
- **gitlab-ci:** enforce 'coverage' runs tool's 'src' sources only ([d5a9ea2](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/d5a9ea2c3fd2d08efe8230c9cb5e4235929f0b27))
- **gitlab-ci:** add support for '-f [VAR], --flag [VAR]' in 'readme' ([e20bfb6](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/e20bfb637051e8720d3dd5944079a96a3b237325))
- **gitlab-ci:** migrate to 'pre-commit-crocodile/commits@5.0.0' ([e88223a](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/e88223a1cd05baec97984db2ac7d8a38a716ea6f))
- **gitlab-ci:** migrate to 'CI_LOCAL_*' variables with 'gcil' 12.0.0 ([760fb65](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/760fb65cd58b715471c0698aa24e1bce1fc3b517))
- **gitlab-ci:** bind coverage reports to GitLab CI/CD artifacts ([3ae73e3](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/3ae73e3cbe9738bd25a193bcd3e5178370ba49f7))
- **gitlab-ci:** configure 'coverage' to parse Python coverage outputs ([45cad4c](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/45cad4c26d7744ba35838ebcbd9efce3e569b9fc))
- **gitlab-ci:** always run 'coverage:*' jobs on merge requests CI/CD ([1493895](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/149389519bf5b5aba849a7d45b0138ff36596326))
- **gitlab-ci:** show coverage reports in 'script' outputs ([5250252](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/52502520abf7b754beefe2755d46a61cd4fd72ef))
- **gitlab-ci:** restore Windows coverage scripts through templates ([40c3a2b](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/40c3a2b9b1305efedd5e5a36318e60469223d0f9))
- **gitlab-ci:** resolve 'coverage' regex syntax for Python coverage ([4fce42f](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/4fce42f28592f9ae30614d1c1815ce13c63be2c6))
- **gitlab-ci:** resolve 'coverage:windows' relative paths issues ([f4ca545](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/f4ca5459554dd9049d9b6dbbb9e463e832c34670))
- **gitlab-ci:** run normal 'script' in 'coverage:windows' with 'SUITE' ([54ed65a](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/54ed65a6100222715d1a3195896e6f5fc7741b7d))
- **gitlab-ci:** use 'before_script' from 'extends' in 'coverage:*' ([23e7c1e](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/23e7c1ed0a0e8aa04d3eb35c57e48d0554f5e1ab))
- **gitlab-ci:** run 'versions' tests on 'coverage:windows' job ([171ba60](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/171ba6005ade03f4fccd88f0b3145c68ddc0d82c))
- **gitlab-ci:** fix 'pragma: windows cover' in 'coverage:linux' ([584537d](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/584537defc5f3393097743adc00ad559c5f62e38))
- **gitlab-ci:** add 'pragma: ... cover file' support to exclude files ([5617699](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/56176994a9ab82f3b329f922faa8b10c80ede10f))
- **gitlab-ci:** isolate 'pages' and 'pdf' to 'pages.yml' template ([28ed737](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/28ed7374f5c35eea488b4ff66e99b1329e5ef370))
- **gitlab-ci:** isolate 'deploy:*' jobs to 'deploy.yml' template ([131c168](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/131c16847c72195479468440f09dd4426c0c2472))
- **gitlab-ci:** isolate 'sonarcloud' job to 'sonarcloud.yml' template ([9d7d564](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/9d7d5647bc999ad0e1f82a82415b0f08533ebdf6))
- **gitlab-ci:** isolate 'readme' job to 'readme.yml' template ([4225b1f](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/4225b1f2ddb1fbf50ee79dd549f665956426c8d9))
- **gitlab-ci:** isolate 'install' job to 'install.yml' template ([5c0343c](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/5c0343c25004c7948f5937e33d4d0ce9e0553abe))
- **gitlab-ci:** isolate 'registry:*' jobs to 'registry.yml' template ([d84bd44](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/d84bd44fbdfe35219d123f6a0778f408f1ac45e5))
- **gitlab-ci:** isolate 'changelog' job to 'changelog.yml' template ([7785753](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/778575316f2f5c09c8bbea2ffc36c3fac49bb6b1))
- **gitlab-ci:** isolate 'build' job to 'build.yml' template ([4ab1b48](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/4ab1b48cf77e10420914f5cfd22c898d86ebb48b))
- **gitlab-ci:** isolate 'codestyle' job to 'codestyle.yml' template ([72af2d5](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/72af2d59729aa69b39310824a335db046c3af1ee))
- **gitlab-ci:** isolate 'lint' job to 'lint.yml' template ([8da165a](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/8da165ae03fba919375895741b793c8c9f694b9e))
- **gitlab-ci:** isolate 'typings' job to 'typings.yml' template ([e62276e](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/e62276ed53a210addb4933816a680293f51ef535))
- **gitlab-ci:** create 'quality:coverage' job to generate HTML report ([94e6d7a](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/94e6d7a92e8c2ba6bbf4d11e039bd018fd03e594))
- **gitlab-ci:** cache HTML coverage reports in 'pages' ([ce854a3](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/ce854a3f4220ddeb40935498e0fc77d5038b0299))
- **gitlab-ci:** migrate to 'quality:sonarcloud' job name ([b74dfa7](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/b74dfa743ba886c40d055f6429806059de646ceb))
- **gitlab-ci:** isolate 'clean' job to 'clean' template ([b24f72d](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/b24f72d012cff2cdb537ce37dc043bd905b5de87))
- **gitlab-ci:** deprecate 'hooks' local job ([8b2dd9f](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/8b2dd9f90c730be60a19ec8726138f8edee7a952))
- **gitlab-ci:** use more CI/CD inputs in 'pages.yml' template ([bfe0140](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/bfe01401b3a73342232cbde8804aa9f8da37928c))
- **gitlab-ci:** isolate 'preview' to 'preview.yml' template ([79d9505](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/79d950579e80b61c1b346e1a4f9d866975997422))
- **gitlab-ci:** isolate '.test:template' to 'test.yml' template ([b6a3451](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/b6a34511b6cc72a8c89b1a84e52d45ceeb9ea352))
- **gitlab-ci:** isolate '.coverage:*' to 'coverage.yml' template ([c34ab2f](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/c34ab2f6c3b56544d4537d8aafe60de7e84bc1db))
- **gitlab-ci:** raise latest Python test images from 3.12 to 3.13 ([374a279](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/374a2795bcc3d623983886ef2763b484536a832b))
- **gitlab-ci:** migrate to RadianDevCore components submodule ([bb2a3cc](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/bb2a3cc46a9db8b99d120ff1231ff13b2b69cbaa))
- **gitlab-ci:** isolate Python related templates to 'python-*.yml' ([fb1353a](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/fb1353a4e2bd1d292546080086f97e0a334cb32f))
- **gitlab-ci:** migrate to 'git-cliff' 2.9.1 and use CI/CD input ([e909493](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/e9094935fdf6d350a40a5deadd713f0eb330c68e))
- **gitlab-ci:** create 'paths' CI/CD input for paths to cleanup ([946d5dc](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/946d5dc58c5f4155d406a50775df687b59a72cdf))
- **gitlab-ci:** create 'paths' CI/CD input for paths to format ([bb20ef7](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/bb20ef7c3adf7adb2623a2254a4110c7698997e4))
- **gitlab-ci:** create 'paths' CI/CD input for paths to check ([4dd2b40](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/4dd2b408791442ca02cb33ce530940a9d987bbe9))
- **gitlab-ci:** create 'paths' CI/CD input for paths to lint ([4695862](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/469586270e1fa2a9a44f8655e4a05308d6e8e93d))
- **gitlab-ci:** create 'intermediates' and 'dist' CI/CD inputs ([b87d487](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/b87d487298bf931c076d6ea1336019641bf44e57))
- **gitlab-ci:** minor YAML improvement on '.test:docker' template ([95f7d09](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/95f7d098f96152250586a5910f1f173c788e9082))
- **gitlab-ci:** implement GitLab tags protection jobs ([b67fed7](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/b67fed77ddd779e683d1b0f9af74c79265b36087))
- **gitlab-ci:** remove redundant 'before_script:' references ([7f02806](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/7f02806fd48519ae3dc90ca29a46f9f468919746))

### 📦 Build

- **containers/rehost:** revert to Debian 12 'python:3.13-slim-bookworm' ([583000d](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/583000dce0a71ffe66f5cf60965267f4c09e4cb6))
- **pages:** install 'coverage.txt' requirements in 'pages' image ([bd77ba3](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/bd77ba311ad7f85c276ab20bcfdc0f39967c59fd))
- **requirements:** add 'importlib-metadata' runtime requirement ([1351466](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/135146626a6d31754116086fc475ce820e282687))
- **requirements:** migrate to 'commitizen' 4.8.2+adriandc.20250608 ([de087ab](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/de087abf17f612a0ef0a597247090381be2f5e96))
- **requirements:** migrate to 'gcil' version 12.0.0 ([92fa0d3](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/92fa0d3c3278861dcc0631e1835d93dd628224db))
- **requirements:** install 'mkdocs-coverage>=1.1.0' for 'pages' ([cc01f83](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/cc01f8307c7fc8276b197c4ffddd77f71e45e991))
- **requirements:** upgrade to 'playwright' 1.54.0 ([18df933](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/18df933a507e1ea0673f9be38b21ccd20472bc7b))


<a name="4.3.0"></a>
## [4.3.0](https://gitlab.com/RadianDevCore/tools/pexpect-executor/compare/4.2.0...4.3.0) (2025-01-01)

### 🐛 Bug Fixes

- **cli:** use package name for 'Updates' checks ([636c1f4](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/636c1f4994dde75f2340728136223b2af3c850dc))

### 📚 Documentation

- **mkdocs:** minor '(prefers-color-scheme...)' syntax improvements ([a1d55bf](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/a1d55bfdadd201bf606cf62657856cc2d8466ba5))
- **mkdocs, pages:** use 'MKDOCS_EXPORTER_PDF_OUTPUT' for PDF file ([9d7721a](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/9d7721a5eb3c7aa858bd5ee34996623f73cd208c))
- **pages:** rename PDF link title to 'Export as PDF' ([87d1b0a](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/87d1b0a2ce4c6b043f0f9655c0cb8da1c925be14))
- **pdf:** avoid header / footer lines on front / back pages ([6c9c8dc](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/6c9c8dcca64a36f66c11a548e9ddcc85d58a5236))
- **pdf:** minor stylesheets codestyle improvements ([80f3b4f](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/80f3b4f339f4e8bd6d755a1d629d06382ef90740))
- **pdf:** reverse PDF front / back cover pages colors for printers ([cc66565](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/cc66565c4d96c9fc49836182a05cec3a20916a03))
- **prepare:** use 'mkdocs.yml' to get project name value ([db8bf2e](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/db8bf2eb14a9e6f5f2b8c7f4187cc5d13ac6195d))
- **readme:** add missing 'NO_COLOR=1' documentation section ([90aea96](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/90aea968f13922d3355bb206dd3b670a0676b731))
- **stylesheets:** resolve lines and arrows visibility in dark mode ([897553e](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/897553e49cce0e23804653cf39d0df92aae593d4))
- **templates:** add 'Author' and 'Description' to PDF front page ([aff2809](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/aff28096f3123107b6d556b8af41bf019915576e))
- **templates:** add 'Date' detail on PDF front page ([2e2969d](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/2e2969dfc3688601db80372d07a27a53d59009a9))
- **templates:** use Git commit SHA1 as version if no Git tag found ([5ba91c9](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/5ba91c9410866e96e814c700cc5fa2e48589e7d2))

### ⚙️ Cleanups

- **src, readme:** minor codestyle and syntax improvements ([ad86d6d](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/ad86d6ddc43c67533580d555c1bb62446c9c9b78))

### 🚀 CI

- **gitlab-ci:** avoid PDF slow generation locally outside 'pdf' job ([571c59c](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/571c59c49dd916a4eaab99fbd523b287ad52c1bd))
- **gitlab-ci:** validate host network interfaces support ([b087fcb](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/b087fcb8f6b093d06a388f407f3db2bbffeff0a2))
- **gitlab-ci:** enable '.local: no_regex' feature ([667b21f](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/667b21f97ed0d0627a5cc52d57008926489b862a))
- **gitlab-ci:** append Git version to PDF output file name ([8e7ee7e](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/8e7ee7ef629dcf3d482f234d4a466db5e02c71f0))
- **gitlab-ci:** rename PDF to 'pexpect-executor' ([6be2a09](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/6be2a09f6239dadc2120885b50e3d411a276e44e))
- **gitlab-ci:** migrate to 'pre-commit-crocodile/commits@4.0.0' ([6a67ca1](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/6a67ca1f6957ae86f9f9f50a3076e78ae05e3107))
- **gitlab-ci:** ensure 'pages' job does not block pipeline if manual ([15da3b8](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/15da3b8fecbec3506e52c231303cd07ef4d83a0b))
- **gitlab-ci:** change release title to include tag version ([ce57639](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/ce576390eca75a677359be7e3e2ce02b391a0273))


<a name="4.2.0"></a>
## [4.2.0](https://gitlab.com/RadianDevCore/tools/pexpect-executor/compare/4.1.1...4.2.0) (2024-10-28)

### 🐛 Bug Fixes

- **main:** ensure 'FORCE_COLOR=0' if using '--no-color' flag ([2a0184b](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/2a0184b75c46b80c1522571c0ff807612f2b1fd4))

### 📚 Documentation

- **assets:** prepare mkdocs to generate mermaid diagrams ([1a2a4c7](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/1a2a4c719474f80043157209db874f3912c252f9))
- **cliff:** improve 'Unreleased' and refactor to 'Development' ([a2284e4](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/a2284e45880acab942ea1b697737e3eab4fba719))
- **covers:** resolve broken page header / footer titles ([1827848](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/18278485e3b68965a7a4f74fffcd9c5f891f9969))
- **custom:** change to custom header darker blue header bar ([e13bcbe](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/e13bcbe89f73e1247d4e086d6f1796cd5153ad6a))
- **docs:** improve documentation PDF outputs with page breaks ([bcf09c6](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/bcf09c6b9abad5e664101f3a96897efb93f21150))
- **mkdocs:** enable 'git-revision-date-localized' plugin ([e0bd4a6](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/e0bd4a648c04a148410a2f8f9452e52817d70037))
- **mkdocs:** change web pages themes colors to 'blue' ([8e9e4b3](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/8e9e4b3cd78c137cd3971f898218f538dd008c8f))
- **mkdocs:** fix 'git-revision-date-localized' syntax ([23e89c7](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/23e89c7a063709d573e45c0a290624ef26786d4f))
- **mkdocs:** migrate to 'awesome-pages' pages navigation ([847730d](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/847730d6e65a085326d83e58bdcfb347ada0113c))
- **mkdocs:** change 'auto / light / dark' themes toggle icons ([5b1acd1](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/5b1acd1fa371d1ea86d7c86ab3825e15bde3a0a7))
- **mkdocs:** enable and configure 'minify' plugin ([e4f1a48](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/e4f1a48aa5cbe3053aa36b8faf3895b28a3806e0))
- **mkdocs:** install 'mkdocs-macros-plugin' for Jinja2 templates ([518c318](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/518c31861e26dd6885aecc5e4de3b93d9fee84a3))
- **mkdocs:** enable 'pymdownx.emoji' extension for Markdown ([6456d8e](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/6456d8e1451e18730bfca88f37b379b50ec45066))
- **mkdocs:** implement 'mkdocs-exporter' and customize PDF style ([943d8b3](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/943d8b34c2d11a441276e1d040a03cf44957e90b))
- **mkdocs:** set documentation pages logo to 'solid/code' ('</>') ([45e5950](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/45e595078e59dee06684a832835cd52cabb0a9ab))
- **mkdocs:** enable 'permalink' headers anchors for table of contents ([9749ac5](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/9749ac526bdc4a75f0729f8cded82e15535b441b))
- **mkdocs:** prepare 'privacy' and 'offline' plugins for future usage ([311727e](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/311727e6833eda5f15f7c8094f7743b2308375ca))
- **mkdocs:** disable Google fonts to comply with GDPR data privacy ([a248fbc](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/a248fbcfd50daad9dc7c916744bdd00fc8597149))
- **mkdocs:** implement 'Table of contents' injection for PDF results ([b40d619](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/b40d6193150ebe39bf325af6f2fab2cfdcaee83d))
- **mkdocs:** enable 'Created' date feature for pages footer ([bc27801](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/bc278017e15fda72059076b6aa65d7f73b140d54))
- **mkdocs:** add website favicon image and configuration ([719970d](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/719970dc8b52032201ef8b6cea4c4088351b6c6c))
- **mkdocs:** implement 'book' covers to have 'limits' + 'fronts' ([6d9f4ce](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/6d9f4ce798f2f7eaa3ce2c076929b611eb7e5025))
- **mkdocs:** isolate assets to 'docs/assets/' subfolder ([43ffd28](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/43ffd28256f1112397f178e70757812a1b0032d8))
- **mkdocs:** exclude '.git' from watched documentation sources ([f4635a8](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/f4635a8b6ee6157d6d020364cb5627b8fcf36ff6))
- **mkdocs, prepare:** resolve Markdown support in hidden '<details>' ([3d1f058](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/3d1f058cc2ac1961f99d377f402007cfb2a294a7))
- **pages:** rename index page title to '‣ Usage' ([1f35dd9](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/1f35dd97482c2ce779322f92182a19234ade8277))
- **pdf:** simplify PDF pages copyright footer ([a1b0ab7](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/a1b0ab7ed6fe1e9d85bc6e7a2b5d4d8fa58b528c))
- **pdf:** migrate to custom state pseudo class 'state(...)' ([b7e2e4b](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/b7e2e4bd520e41367b79d6dd02c71092915888dc))
- **prepare:** regenerate development 'CHANGELOG' with 'git-cliff' ([9432be3](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/9432be3bf344708e1eedcc3e294663dab8770823))
- **prepare:** avoid 'md_in_html' changes to 'changelog' and 'license' ([7b52cc5](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/7b52cc5f6244fc0452eda46865fb85103e989eb2))
- **prepare:** fix '<' and '>' changelog handlings and files list ([a63a883](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/a63a883f5618056fdf5a3a0fc423fffc16580518))
- **prepare:** implement 'About / Quality' badges page ([b6af8f4](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/b6af8f4f4b0299780386d5ffc1b0c85d6feee884))
- **prepare:** improve 'Quality' project badges to GitLab ([b4f2d07](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/b4f2d07c81b0a4dc37aa5bcb55b475cd6ee78334))
- **prepare:** use 'docs' sources rather than '.cache' duplicates ([36c81b0](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/36c81b03db371f574983f92b6723dd7afeae356c))
- **prepare:** resolve 'docs/about' intermediates cleanup ([221a8a6](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/221a8a671f1d21d213dc3cbb8a48bef4ec880839))
- **prepare:** add PyPI badges and license badge to 'quality' page ([a4525bc](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/a4525bc2cc09208bec7c33464dcf1fce8dcf09f0))
- **prepare:** avoid adding TOC to generated and 'no-toc' files ([1bcbeb9](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/1bcbeb9dca3af48ffd097c517c59a78f3839c8db))
- **readme:** add 'gcil:enabled' documentation badge ([36c6df7](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/36c6df76bc0e60c963a234a52e9c16ebb5189a28))
- **readme:** add pypi, python versions, downloads and license badges ([8e6fbaa](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/8e6fbaaf98172c3533201cd0e07f30cf548bd569))
- **robots:** configure 'robots.txt' for pages robots exploration ([08a1ab8](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/08a1ab83158c8abb1f000aa890e92e55f1b11683))

### ⚙️ Cleanups

- **gitignore:** exclude only 'build' folder from sources root ([837518d](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/837518da6bb04697007bc0062b467933cc5de83c))
- **gitignore:** exclude '/build' folder or symlink too ([8bb724c](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/8bb724cfe03a57ae21601f9f7b269aab4abe670e))
- **lib:** resolve 'too-many-positional-arguments' new lint warnings ([3526746](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/3526746ee424db3062481c4ba4f722c0d8f03898))
- **sonar:** wait for SonarCloud Quality Gate status ([45700f7](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/45700f7f7e86c08ab5e42043078bade56727b321))
- **vscode:** use 'yzhang.markdown-all-in-one' for Markdown formatter ([f6a4191](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/f6a4191fdeab50b813f84d532698a685040a9cdc))

### 🚀 CI

- **gitlab-ci:** prevent 'sonarcloud' job launch upon 'gcil' local use ([53ad66b](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/53ad66bf4192cbfce98f41c2ba348023ec439818))
- **gitlab-ci:** run SonarCloud analysis on merge request pipelines ([174d1d0](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/174d1d00904395d8c379f86f2a32186045b49ed5))
- **gitlab-ci:** watch for 'config/*' changes in 'serve' job ([3824631](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/3824631e104e5cf660ae0a310379ecece8eb73bb))
- **gitlab-ci:** fetch Git tags history in 'pages' job execution ([33e1861](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/33e186110026473eb4654ed1da5ce3b6e37aa5ed))
- **gitlab-ci:** fetch with '--unshallow' for full history in 'pages' ([446049b](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/446049b91d24dadf47d7500726a41870c4ee55c8))
- **gitlab-ci:** enforce 'requirements/pages.txt' in 'serve' job ([6be321d](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/6be321d1840fbc20924a17a5ff48f3d6b35d0964))
- **gitlab-ci:** add 'python:3.12-slim' image mirror ([b2927d6](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/b2927d690c0ffe74d24e7a008ae516dd0f68245b))
- **gitlab-ci:** inject only 'mkdocs-*' packages in 'serve' job ([0cb163e](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/0cb163e10cc08ef6495f751ef96887514f9feeae))
- **gitlab-ci:** install 'playwright' with chromium in 'serve' job ([221e1e9](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/221e1e9814004966e912e9910e60946520b5002a))
- **gitlab-ci:** find files only for 'entr' in 'serve' ([29615a5](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/29615a5ab8614bfadd65d48ca4253125f67a1da1))
- **gitlab-ci:** improve GitLab CI job outputs for readability ([fb533a4](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/fb533a4fd82746438a548987ecdad6d14913a995))
- **gitlab-ci:** deploy GitLab Pages on 'CI_DEFAULT_BRANCH' branch ([fdc2075](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/fdc2075eecc4f2cd16a757957a61b20b59257af5))
- **gitlab-ci:** ignore 'variables.scss' in 'serve' watcher ([5e4b48b](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/5e4b48b69e838c8c67687a7ff3d519992d67d6a7))
- **gitlab-ci:** preserve only existing Docker images after 'images' ([1148124](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/11481244fa58d29ba9a26bf6267e48ef2d93cada))
- **gitlab-ci:** use 'MKDOCS_EXPORTER_PDF_ENABLED' to disable PDF exports ([009b822](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/009b822b2872c8db7ab03dcb661c410e05a5393f))
- **gitlab-ci:** run 'pages' job on GitLab CI tags pipelines ([b53f01e](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/b53f01e62649d57fdb0251027ca0bb531546a1e1))
- **gitlab-ci:** isolate 'pages: rules: changes' for reuse ([a7d57c6](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/a7d57c62e9197b3c08b88b4c09565efb86ae6230))
- **gitlab-ci:** allow manual launch of 'pages' on protected branches ([2fd245c](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/2fd245cd8cad9a86d21406a20e37fc3b672f7984))
- **gitlab-ci:** create 'pdf' job to export PDF on tags and branches ([2c38595](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/2c385951d72936a1e050d3ba15ee946ce9f745d5))
- **gitlab-ci:** implement local pages serve in 'pages' job ([7b381fe](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/7b381fee207ba15111c2d01aeed06d5b0208b7ef))
- **gitlab-ci:** raise minimal 'gcil' version to '11.0' ([547c609](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/547c60964548d023cbcfba975b0f968e23cc9603))
- **gitlab-ci:** enable local host network on 'pages' job ([9567f7b](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/9567f7b3c3bdee036ae82df1c229ab7f1ff8c0b8))
- **gitlab-ci:** detect failures from 'mkdocs serve' executions ([26a100a](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/26a100a1cbe211eb08d22bb5df1906a19a681a3d))
- **gitlab-ci:** refactor images containers into 'registry:*' jobs ([3bf19bf](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/3bf19bf7564f21017ef0680977e40c37a767cb79))
- **gitlab-ci:** bind 'registry:*' dependencies to 'requirements/*.txt' ([53d6987](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/53d69875b21815d80cfb7ee07a1a7d02dc2c0810))

### 📦 Build

- **build:** import missing 'build' container sources ([9d6af69](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/9d6af6996c93239af79d05e923dd647da1086b80))
- **containers:** use 'apk add --no-cache' for lighter images ([4798842](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/479884232601e8d593acc4400b6408d5da7ae80f))
- **pages:** add 'git-cliff' to the ':pages' image ([80caf7f](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/80caf7f0a4f1ea4d678d44a27778f86bfdae23bf))
- **pages:** migrate to 'python:3.12-slim' Ubuntu base image ([4a17f92](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/4a17f92487c6989b58d4bd8a82e8300ac630e4ce))
- **pages:** install 'playwright' dependencies for 'mkdocs-exporter' ([a08909f](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/a08909fb8d775163cce986858172b09e59e2b552))
- **pages:** install 'entr' in the image ([57ba5e8](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/57ba5e8cf47b0f0e20960ab066ded4fb2416c3cf))
- **requirements:** install 'mkdocs-git-revision-date-localized-plugin' ([0e4a74a](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/0e4a74ad4927e59ca6255da76a15002d56757ea6))
- **requirements:** install 'mkdocs-awesome-pages-plugin' plugin ([d4a190b](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/d4a190bd686fad21edf32ded1f5320b7b84e85a2))
- **requirements:** install 'mkdocs-minify-plugin' for ':pages' ([5ce53e7](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/5ce53e735f629d06b35c38f48850cab7e40b72bc))
- **requirements:** install 'mkdocs-exporter' in ':pages' ([7725c69](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/7725c69600ce51cee25d236664c33b1049f2f157))
- **requirements:** migrate to 'mkdocs-exporter' with PR#35 ([cad1ef8](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/cad1ef8edd882b65f8fcd77dd5b114cabcec4800))
- **requirements:** upgrade to 'playwright' 1.48.0 ([3d700a0](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/3d700a05c83fe5fb6a75d67ce46721d34bcc7c9e))
- **requirements:** migrate to 'mkdocs-exporter' with PR#42/PR#41 ([e72acae](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/e72acae4e78e57fa1ff6a7e228aa629283ca4a2c))


<a name="4.1.1"></a>
## [4.1.1](https://gitlab.com/RadianDevCore/tools/pexpect-executor/compare/4.1.0...4.1.1) (2024-08-25)

### ✨ Features

- **updates:** migrate from deprecated 'pkg_resources' to 'packaging' ([b32d414](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/b32d414e6b3fc43543a65b0f016715fbcdba0a6b))

### 📚 Documentation

- **mkdocs:** implement GitLab Pages initial documentation and jobs ([2f4d1e7](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/2f4d1e7e1c85d746bbd8c06371f6f033c42802d0))
- **readme:** link against 'gcil' documentation pages ([53c4691](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/53c4691d7c58d42b0f6e694388cc94a7e940cc76))

### ⚙️ Cleanups

- **commitizen:** migrate to new 'filter' syntax (commitizen#1207) ([d391f83](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/d391f8330f1e12cadbf257f4fa1870f60f89f8c7))
- **pre-commit:** add 'python-check-blanket-type-ignore' and 'python-no-eval' ([5a185d6](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/5a185d6916eb947f058ac9be32e5c668ec222590))
- **pre-commit:** fail 'gcil' jobs if 'PRE_COMMIT' is defined ([4e68d10](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/4e68d100298e454dc5fd191b2aa728efa59d92e4))
- **pre-commit:** simplify and unify 'local-gcil' hooks syntax ([9b07376](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/9b07376ef4f3298aa804ba584a4b687ad77d2d0a))
- **pre-commit:** improve syntax for 'args' arguments ([dca4bad](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/dca4bad099b39836dc9d6527f043f92d1e7df7e5))
- **pre-commit:** migrate to 'run-gcil-*' template 'gcil' hooks ([0397040](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/0397040bbd6549621c62af50b6588604c0d92f56))
- **pre-commit:** update against 'run-gcil-push' hook template ([6f6bcad](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/6f6bcada0470f82a4f67576e3ae7651bb5d8dc5f))
- **pre-commit:** migrate to 'pre-commit-crocodile' 3.0.0 ([e5d8e8f](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/e5d8e8fdd7076150b73b25e340f21ed8c58e23e3))

### 🚀 CI

- **containers:** implement ':pages' image with 'mkdocs-material' ([e776f10](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/e776f107399b6c035ff1ab683bac4da1b006ce86))
- **gitlab-ci:** avoid failures of 'codestyle' upon local launches ([d42bd70](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/d42bd704d918e77529f6f7976bfd031d83c5e8ac))
- **gitlab-ci:** migrate to 'pre-commit-crocodile/commits@2.1.0' component ([9558e4a](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/9558e4ad644e6075e0429fdd6cda538e5f6f8bdb))
- **gitlab-ci:** migrate to 'pre-commit-crocodile/commits@3.0.0' component ([e72fa3c](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/e72fa3c5f1a76d16258e79f3bf25ddd5dc6b53b1))


<a name="4.1.0"></a>
## [4.1.0](https://gitlab.com/RadianDevCore/tools/pexpect-executor/compare/4.0.1...4.1.0) (2024-08-21)

### 📚 Documentation

- **readme:** migrate to 'RadianDevCore_pexpect-executor' project key ([2c7c04e](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/2c7c04eb09d138d5bd642a7243281abe521c587e))
- **readme:** link 'gcil' back to 'gitlabci-local' PyPI package ([49566cc](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/49566ccf0ca5a8aa4f6b1d735a0ea8ff3aea39db))

### ⚙️ Cleanups

- **commitizen:** migrate to 'pre-commit-crocodile' 2.0.1 ([a5c0162](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/a5c0162ce90435476a12958ab761b6ed55e3dfd7))
- **pre-commit:** migrate to 'pre-commit-crocodile' 2.0.0 ([421463c](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/421463c836fa2612e924d6054b15aaca08c6109a))
- **sonar-project:** migrate to 'RadianDevCore_pexpect-executor' project key ([ffa8d86](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/ffa8d869700907b1e11d1d9f88685ef867359ab0))

### 🚀 CI

- **gitlab-ci:** detect and refuse '^wip|^WIP' commits ([f5276bb](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/f5276bbcf3acc9e732a286971cc5717519bb4a5c))
- **gitlab-ci:** isolate 'commits' job to 'templates/commit.yml' ([ef4ca7b](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/ef4ca7b73e72be2ed159ecc61996b7c207221af2))
- **gitlab-ci:** migrate to 'pre-commit-crocodile/commits@2.0.0' component ([d597149](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/d597149d510666d8694e0c3f102d56598c28b74f))
- **gitlab-ci:** create 'hooks' local job for maintenance ([8846bb6](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/8846bb60c0cfd009cf7dac7d560412ed30e61af4))


<a name="4.0.1"></a>
## [4.0.1](https://gitlab.com/RadianDevCore/tools/pexpect-executor/compare/4.0.0...4.0.1) (2024-08-20)

### 🐛 Bug Fixes

- **executor:** fix 'KEY_HOME' variable for 'xterm' support ([e2b8103](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/e2b810364a52e6c3456886dc5f44c3555e6a6930))


<a name="4.0.0"></a>
## [4.0.0](https://gitlab.com/RadianDevCore/tools/pexpect-executor/compare/3.2.0...4.0.0) (2024-08-20)

### ✨ Features

- **executor:** implement most actions, Ctrl+? and F? keyboard keys ([26bb859](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/26bb859bddf83e14f0f83bd8793ae7232385bb76))
- **🚨 BREAKING CHANGE 🚨 |** **setup:** drop support for Python 3.6 ([73bfbda](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/73bfbda1ac6765f5b46d390c833ca81a9a9247cd))
- **🚨 BREAKING CHANGE 🚨 |** **setup:** drop support for Python 3.7 ([8b19670](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/8b196704c0e8febc7fcda12d080ab805081ce2ae))

### 🐛 Bug Fixes

- **package:** fix package name for 'importlib' version detection ([4d658ad](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/4d658adb974e4fe4d9076ce222a1a0f2cc710c07))
- **platform:** always flush on Windows hosts without stdout TTY ([d84330e](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/d84330ee356353ca4049124095bddb7b4383c61f))

### 📚 Documentation

- **readme:** add 'pre-commit enabled' badges ([65b30be](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/65b30befa59bc179cc74fe83df95e34b2157d99c))

### ⚙️ Cleanups

- **gitattributes:** always checkout Shell scripts with '\n' EOL ([2396648](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/23966482cc80aca77ae6f347fb9d36ca92ea50b6))
- **gitignore:** ignore '.*.swp' intermediates 'nano' files ([e4e5a71](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/e4e5a7126a6aedc60746f855a3a512391a3e64e4))
- **hooks:** implement evaluators and matchers priority parser ([8cc5587](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/8cc558732959beb7fafe03e9c0856c391e5005a3))
- **pre-commit:** run 'codestyle', 'lint' and 'typings' jobs ([f46e9b7](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/f46e9b778c2fbb86639e6611a4833321b9ba607a))
- **pre-commit:** migrate to 'pre-commit-crocodile' 2.0.0-db6f0f8 ([98be58f](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/98be58f7de1196d87192850ace0a88202bf0f3dc))

### 🚀 CI

- **gitlab-ci:** show fetched merge request branches in 'commits' ([10dd024](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/10dd02483f761f7a17557c87e6e62cc3c0ce9caa))
- **gitlab-ci:** fix 'image' of 'commits' job ([39f92f2](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/39f92f2f2d7b2c415572b1413df4219ddef977b2))
- **gitlab-ci:** always run 'commits' job on merge request pipelines ([70ee165](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/70ee165b3547d0e2c922a1000456f0c2fe398820))
- **gitlab-ci:** make 'needs' jobs for 'build' optional ([ee8818b](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/ee8818bb3d3f3719f752df72134bbf259904c795))
- **gitlab-ci:** validate 'pre-commit' checks in 'commits' job ([31ba900](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/31ba900b2b7f710f8066741718d805bb4b399218))
- **gitlab-ci:** set 'DEBUG_UPDATES_DISABLE' for faster offline tests ([00414c5](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/00414c5340e6f3aa2282453bb601dc687298dae0))
- **gitlab-ci:** migrate Windows tests to Python 3.10 using 'pywine:3.10' ([f4b2e6e](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/f4b2e6e58c1037b3a3bdd0d5494e4433f56b640c))
- **gitlab-ci:** migrate to 'pipx' installations on hosts tests ([e739ae8](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/e739ae83db16a3d19b022a063e0210a348a64e56))
- **gitlab-ci:** raise oldest Python test images from 3.6 to 3.7 ([c27963a](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/c27963a621b93448b573ad7bf70f105e09804538))
- **gitlab-ci:** raise oldest Python test images from 3.7 to 3.8 ([f3fe599](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/f3fe5995232845fdf244cf431ab6184a6c8f0024))
- **gitlab-ci:** refactor images into 'containers/*/Dockerfile' ([b388690](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/b38869033929ba310e3945de4ba73f95538fa923))
- **gitlab-ci:** use 'HEAD~1' instead of 'HEAD^' for Windows compatibility ([081fae1](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/081fae1ac8e3eb76e957a1e762e4ac3f783c8412))
- **gitlab-ci:** check only Python files in 'typings' job ([fd88b8b](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/fd88b8b681999dd6cd5e0cee8fabef1459b7d34a))

### 📦 Build

- **pre-commit:** migrate to 'pre-commit-crocodile' 1.1.0 ([1265e86](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/1265e865b1e161e33935c48e009efad6f87eeed1))
- **requirements:** migrate to 'gitlabci-local' version 10.0.1 ([64bf4be](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/64bf4be8c4e6340743e28cfdf9deceb255fbdff8))


<a name="3.2.0"></a>
## [3.2.0](https://gitlab.com/RadianDevCore/tools/pexpect-executor/compare/3.1.0...3.2.0) (2024-08-15)

### 🐛 Bug Fixes

- **setup:** refactor 'python_requires' versions syntax ([68ffa95](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/68ffa95afa97f2bf2342c93ed7ff202066f35253))
- **setup:** resolve project package and name usage ([868f108](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/868f108ed842a5006e6f296d2c0254e049c9601b))
- **updates:** ensure 'DEBUG_UPDATES_DISABLE' has non-empty value ([afe2987](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/afe2987a0edea60c876bbac35b876197b6297591))
- **updates:** fix offline mode and SemVer versions comparisons ([665258e](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/665258e308ea53bfdc68bce18fd710b0b8c96426))

### 📚 Documentation

- **cliff:** use '|' to separate breaking changes in 'CHANGELOG' ([c13b1eb](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/c13b1eb7c0e8422cfaaa4f7c5f3c570d35ce16c3))
- **license:** update copyright details for 2020-2024 ([74db417](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/74db417e526d711656305ab92f85284774d3640e))
- **readme:** add 'Commitizen friendly' badge ([2d2a73f](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/2d2a73f9d94b7da1ada42d3ad64d68964adea40e))

### 🎨 Styling

- **commitizen, pre-commit:** implement 'commitizen' custom configurations ([fcac530](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/fcac530096f4e6a037055efe7084bd9815072891))
- **pre-commit:** implement 'pre-commit' configurations ([4e9a3e8](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/4e9a3e8cbc5e777492f18cd5fc2e32e9422f7bba))

### 🧪 Test

- **versions:** fix current package version for coverage ([622100e](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/622100eb0f574c8ccb89d573a0262f3e18a689ee))

### ⚙️ Cleanups

- **cli:** disable 'too-many-branches' warning on 'main' function ([583c8bb](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/583c8bbf6677d6ecd79c3d0ea9f3ca77f895c3f1))
- **cli, package:** minor Python codestyle improvements ([a5f9a54](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/a5f9a5484f1241edc807e3e90b6a6f81f7d67f5a))
- **mypy:** convert 'mypy.ini' configuration to Linux EOL ([c727971](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/c72797161674481e569771137a0fb17708d09322))
- **pre-commit:** disable 'check-xml' unused hook ([9222d63](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/9222d633dc036236548eeec08f076636a2aaa3f3))
- **pre-commit:** fix 'commitizen-branch' for same commits ranges ([d2d202e](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/d2d202ecc1138f38d6261f6f08e0564d5da62303))
- **setup:** refactor with more project configurations ([d7a53dd](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/d7a53ddcc081b525aa10a7b3be2f0134ea532c0a))
- **updates:** ignore coverage of online updates message ([ec74e07](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/ec74e07f418ddc27d5fb066518b734c2b37c6b27))
- **vscode:** remove illegal comments in 'extensions.json' ([8b69c38](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/8b69c3819d86970c001d5a8316ad3a5147abe196))

### 🚀 CI

- **gitlab-ci:** watch for 'codestyle', 'lint' and 'typings' jobs success ([0c7cfb3](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/0c7cfb3c853de1553e47c5a3120f8f572d5ab942))
- **gitlab-ci:** create 'commits' job to validate with 'commitizen' ([0ae6d81](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/0ae6d8166acd43121a317aea37e0282eb58b08bb))
- **gitlab-ci:** disable 'PYTHONDONTWRITEBYTECODE' for 'coverage:*' tests ([a7fe306](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/a7fe3061f8fa5ca38b18a25fc9b9b32c27983be9))
- **gitlab-ci:** fix 'commits' job for non-default branches pipelines ([51a1ea3](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/51a1ea345b9c2027bf1a682a4b71b70dc2d99962))

### 📦 Build

- **hooks:** create './.hooks/manage' hooks manager for developers ([8b613ab](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/8b613ab084c136695bf6bad280abeca8e123937a))
- **hooks:** implement 'prepare-commit-msg' template generator ([58f4e02](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/58f4e020fa7270d9c5f14d49a74add66af412e1a))
- **pre-commit:** enable 'check-hooks-apply' and 'check-useless-excludes' ([51a36d9](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/51a36d922b64c11e400be0cd0ff2bfae25e391fd))


<a name="3.1.0"></a>
## [3.1.0](https://gitlab.com/RadianDevCore/tools/pexpect-executor/compare/3.0.2...3.1.0) (2024-08-11)

### ✨ Features

- **🚨 BREAKING CHANGE 🚨 |** **actions, executor:** deprecate 'strips' and use 'masks' instead ([d42e7ca](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/d42e7ca05572a12f1cc5ce6901a5e393791cfc7c))
- **cli:** implement '--no-color' to disable colors ([b9623c3](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/b9623c3babd8ec751bca83d766fe4d8e1425d53c))
- **cli, actions:** implement '--mask' to hide specific strings ([4459ba5](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/4459ba5dfebdad0f1d52cb21764db38126587bad))

### 🐛 Bug Fixes

- **updates:** remove unused 'recommended' feature ([d4a5d84](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/d4a5d84e30f932432cc71afa34b42be2f0d042ae))

### 📚 Documentation

- **readme, preview:** migrate from 'gitlabci-local' to 'gcil' ([cf91dcc](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/cf91dcc2b42f40bb9fd48f5f707b99e0681109fa))
- **readme, test:** migrate from 'gitlabci-local' to 'gcil' package ([d04fcfa](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/d04fcfa6e44477db6dbc8481260481f5a4e9e9e7))

### 🧪 Test

- **gcil:** migrate from 'gitlabci-local' to 'gcil' in tests ([374c402](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/374c4020c26ba908a0f44069b0b9ae2210183aa6))
- **macos:** add coverage test for MacOS specific sources ([3aa2904](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/3aa2904565a647a5a941160e774675cfbbe6790e))
- **requirements:** migrate to 'gcil' version 10.0.0 ([2ec607f](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/2ec607fe8254bad695644c3d5694f142cb718b9f))

### ⚙️ Cleanups

- **cli:** resolve unused variable value initialization ([4f73479](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/4f7347963fac635adde023026bc054541b0a4248))
- **colors:** resolve 'pragma: no cover' detection ([505e236](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/505e236945387dea9b05a8900f3dc5030da0d532))
- **coveragerc:** ignore 'preview.py' and 'setup.py' from coverage ([8d2a480](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/8d2a480ecb25bbee5c9343de851f75d0f60dbeb5))
- **docs, setup:** remove faulty '# pragma: exclude file' flag ([7bb21e6](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/7bb21e6d61e60a11c320ad3c1096adbf1bf76370))
- **platform:** disable coverage of 'SUDO' without write access ([9b42d22](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/9b42d22e91ab38c4cad8e5734a654e4df36ea1a6))
- **sonar-project:** remove 'docs' and 'setup.py' sources coverage ([49955a4](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/49955a4f102897e9ffdcd827e9adac3d0758580e))


<a name="3.0.2"></a>
## [3.0.2](https://gitlab.com/RadianDevCore/tools/pexpect-executor/compare/3.0.1...3.0.2) (2024-08-11)

### 🐛 Bug Fixes

- **executor:** fix library usage missing 'Colors' preparation ([51f438b](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/51f438b03570b592c3db8c8f72ceac6b8f190ab5))
- **package:** check empty 'environ' values before usage ([c771c66](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/c771c66408c30f8e57d8beb5bc0eea7e1ca70741))

### 📚 Documentation

- **preview:** refresh preview SVG presentation ([1366f5b](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/1366f5bfce86d2f8d2e813e65e0638a2a966e651))

### 🚀 CI

- **gitlab-ci:** rehost 'docker:dind' and 'docker:latest' images ([0bcf006](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/0bcf006ea025db1d543e26f07601ac07aac7b5c7))
- **gitlab-ci:** use rehosted 'docker:dind' image for tests ([32f0d04](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/32f0d04293b45586919ecd43de53b6035f597423))
- **gitlab-ci:** install 'bash' in the ':preview' image ([8633c1d](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/8633c1d3f4677b5bad444e36f38b8796552f7efb))
- **gitlab-ci:** remove 'DOCKER_TLS_VERIFY' value for disabled state ([a2aada8](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/a2aada84308301ed3b8200c45b78132d038dc216))
- **gitlab-ci:** migrate to Docker in Docker with TLS certificates ([8b3fdda](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/8b3fdda83f94c469f8110be1d6f89d629ec61de4))
- **gitlab-ci:** set 'FORCE_COLOR' and 'USER' for 'preview' job ([6f4ffb4](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/6f4ffb4c4686fd4a2c73452de5e341a0f70e0fe3))


<a name="3.0.1"></a>
## [3.0.1](https://gitlab.com/RadianDevCore/tools/pexpect-executor/compare/3.0.0...3.0.1) (2024-08-10)

### ✨ Features

- **setup:** add support for Python 3.12 ([3d61681](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/3d61681062a1f0abb832dd4dbc6c8277f4428a3a))

### 📚 Documentation

- **test:** fix URL links codestyle with Markdown syntax ([9227bbf](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/9227bbf7953983b8417a4ea3d5f98d69098b9a55))
- **test:** add installation steps for all test platforms ([11f5897](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/11f58975774c70998ee82b2d5e859267ca678568))
- **test:** use 'pipx' for local installs ([f221975](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/f2219758a0b744cd67efe237c95982b280fc51bd))

### 🎨 Styling

- **main:** declare 'group' variable as '_ArgumentGroup' type ([ac46ffb](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/ac46ffb058d94357c04ea40958e9cd850aa1da95))

### 🧪 Test

- **requirements:** raise 'gitlabci-local' minimal version to 9.1.0 ([d74c23f](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/d74c23f2af12558eb349324822deb57929e3fef3))
- **setup:** disable sources coverage of the build script ([91dbe66](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/91dbe668cb1745f6b07d01aac99a89919da8bbb5))

### 🚀 CI

- **gitlab-ci:** ignore 'docs' changes for tests and coverage jobs ([c6e5596](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/c6e5596c9fbb38a8e1b393ad4abf741d454262a1))
- **gitlab-ci:** define 'DOCKER_TLS_CERTDIR' to default empty value ([7f3be28](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/7f3be28d05332f8c5c696a027f66b29228a3c543))
- **gitlab-ci:** revert to Docker in Docker without TLS certificates ([63a6f9c](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/63a6f9c9c824f6b83fd53201fc26142dc0873a71))
- **gitlab-ci:** raise latest Python test images from 3.11 to 3.12 ([9013601](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/90136012c4c12387157ad7818fccea3bf807266c))
- **gitlab-ci:** deprecate outdated and unsafe 'unify' tool ([a04c921](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/a04c921c323ecd0b858c0cde4689e6d1f235cfe2))


<a name="3.0.0"></a>
## [3.0.0](https://gitlab.com/RadianDevCore/tools/pexpect-executor/compare/2.1.1...3.0.0) (2024-08-10)

### ✨ Features

- **cli:** refactor CLI commands calls into 'entrypoint.py' file ([6f6a44e](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/6f6a44e933bffe769dff55493ad3990039c59464))
- **gitlab-ci, setup:** add support for Python 3.11 ([77e78f4](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/77e78f4e9950c808bb856bd8c587bd4a048fdb55))
- **main:** align 'RawTextHelpFormatter' to 23 chars columns ([b3a86d9](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/b3a86d96c00fd7439213da357952874d898a337c))
- **main:** limit '--help' width to terminal width or 120 chars ([8f361ce](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/8f361ce6dda3398e9291753b7dda8422d9b5fd90))
- **main:** document optional '--' positional arguments separator ([ad9f3f0](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/ad9f3f05f435aef480d10e025401f3f7f690e10c))
- **main, settings:** implement 'Settings' from 'gitlabci-local' ([d35e0b2](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/d35e0b2b73bc6ff74de488916abb6213f23a237e))
- **main, upgrades:** implement 'Upgrades' from 'gitlabci-local' ([fab0327](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/fab0327c67b91a3e9b163126dd5739fa977b9281))
- **package:** add support for standard '__version__' ([18d45f0](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/18d45f04381dde5b31eb797fb61c5d96edf18879))
- **pexpect-executor:** migrate under 'RadianDevCore/tools' group ([b0c203f](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/b0c203f68b88347e341a9c06d96a70cf5b994339))

### 🐛 Bug Fixes

- **cli, colors:** evaluate and prepare colors only upon use ([9c8501a](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/9c8501aa2f7b059c8cc06ddc7b87c6c3c0667d2d))
- **colors:** allow 'colored' library to be missing or unusable ([82d131c](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/82d131cca9037487b7f64a39f4b2f6268ea2ef84))
- **colors:** simplify 'colored' library usage without wrappers ([06b8312](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/06b83123fc1278606b0e8713b9f6c508d9c916f7))
- **colors:** add 'strip' with 'BOLD' and 'RESET' colors last ([bb74c62](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/bb74c6207732197feea4b9c1c1aaed013beb494b))
- **settings:** ensure 'Settings' class initializes settings file ([1bf5964](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/1bf59643fcb7315306d0c6ccfa19022dd4d25034))
- **src:** use relative module paths in '__init__' and '__main__' ([a8292d2](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/a8292d283101e6eac5d094ab1d77da78a5be26fd))

### 🚜 Code Refactoring

- **src:** isolate all sources under 'src/' ([766f04e](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/766f04e1e65269f81e047fe90b13727832ec375a))

### 📚 Documentation

- **cliff:** document 'security(...)' first in changelog ([b7784a9](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/b7784a91c8bce12f83b125ccc953b6cf0ac723f1))
- **setup:** resolve 'Statistics' URL for PyPI documentation ([ee2b1fd](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/ee2b1fd1d97e0dad464cd516e2b040b39aa9cac1))

### 🎨 Styling

- **cli:** refactor codestyle and cleanup against 'gcil' sources ([1cc8e47](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/1cc8e47a0103bb60eff562cf0c7a49ce6807e146))
- **src:** resolve simple standard Python typings ([691ac20](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/691ac201f1ba86eaeb447259ebcd4dfd93f59bb3))

### 🧪 Test

- **docs:** remove 'preview.py' test executions needing deployment ([bd10c8d](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/bd10c8d37935f9ff1aea3449135da7df118ed797))
- **settings:** import 'Settings' class tests from 'gcil' ([76a54e7](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/76a54e711ad425128ba78fa81d6a7b5ba5c897e3))
- **versions:** import 'Updates' class tests from 'gcil' ([7485192](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/748519275d7fb9bea8122707c630e45002e019a0))

### ⚙️ Cleanups

- **docs:** ignore 'import-error' over 'preview.py' ([2c5132a](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/2c5132accc5fc8fbd5b9c735bd8ea750d29159a2))
- **gitlab-ci:** ensure jobs run upon 'requirements/*' changes ([90554dc](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/90554dc762d9d77cd4e8ce90c4d7ec8c9f0c4d56))
- **gitlab-ci:** add 'Install' local job to install built '.whl' ([1f691bc](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/1f691bc55c303512eed4fc3b7b029fd784f5a858))
- **gitlab-ci:** cleanup intermediates and refactor local paths ([48c5e34](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/48c5e3445faa5d9c8158bedec06563c14bd8ca9b))
- **gitlab-ci:** enable signoff of changelog commits ([f37a821](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/f37a8217f5d001e57403e20be4625ab639905cd7))
- **gitlab-ci:** make 'apk' Alpine 'Typing' installation quiet ([09ca62d](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/09ca62d53cad9fd22d7c1614d4b1fbb1d2479f3c))
- **gitlab-ci:** enable mypy colored outputs for readability ([7d03bce](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/7d03bce19d9d4a0602273b818befdd81c6faedd4))
- **run:** deprecate 'run.sh' script for 'gcil' only ([ea60edb](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/ea60edb79ab71986551faab659dd5c92d1b17f24))
- **setup:** add 'setup.py' script shebang header ([ccc019c](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/ccc019c2d693c1c6bd4f8d25368fff7b02f4b54e))
- **sonar-project:** migrate 'sonar.sources' to 'src' sources ([acd78c8](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/acd78c8072cd96f212bf22419eec2650b80de348))
- **src:** ignore 'import-error' over '__init__' and '__main__' ([b6f3bc4](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/b6f3bc4045dac0a706cfb2254fd1004643c25232))
- **vscode:** minor old .gitignore leftover cleanup ([0159417](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/015941725cc3c011d5e8682b6009b86c9840bb77))
- **vscode:** ignore '.tmp.entrypoint.*' files in VSCode ([58cf9ed](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/58cf9ede9e54a813964a98c31cdd54b69066815f))
- **vscode:** configure 'shc' Shell scripts formatting options ([61cf5f2](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/61cf5f29f87e802eb59e149d4e31d33ebc4335e4))
- setup: refactor and unify projet build with constants ([2ee5c90](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/2ee5c900cb022ad4792d99f256c83926d06d901a))
- gitlab-ci: make 'apk add' Alpine installations quiet ([2e9de5b](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/2e9de5b280ec56d2b2a42f5362ce327dfe1b6e75))
- gitlab-ci: add tests successful output and sudo preparation ([b7f351a](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/b7f351ac3f2dc55f8914ef6f16a2a6c201c6f126))
- vscode: configure default formatters for YAML and Markdown ([2cfeb8d](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/2cfeb8d8f1c0efd16795d98efdce0bf1fc77ce21))
- pylint: resolve 'superfluous-parens' new warnings ([e334de8](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/e334de83f3d7172e0cd78559fb5337b30df0db28))

### 🚀 CI

- **gitlab:** support '-p VALUE, --parameter VALUE' in 'readme' job ([fe62114](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/fe62114476a2a5da10eea9fa66e3ce1dc9db49d5))
- **gitlab:** configure Git sources safeties for 'sonarcloud' job ([904fae4](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/904fae473c2c3b6f6999d5324ff3d753cc6baccd))
- **gitlab-ci:** migrate from DockerHub to GitLab project images ([26c41b1](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/26c41b192511494d9131d012a5959f694f37091e))
- **gitlab-ci:** migrate 'git-chglog' from 0.9.1 to 0.15.4 ([13b8b68](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/13b8b6884c9cbec7371d6562f437168a82c00a3c))
- **gitlab-ci:** use 'pipx' for local installs ([03e67b9](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/03e67b95da24b04bac5a6d47a2482532a446de14))
- **gitlab-ci:** isolate 'changelog.sh' to '.chglog' folder ([f782284](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/f78228449dfbf567cc6d496c2fa94ea17871c31d))
- **gitlab-ci:** migrate from 'only: local' to 'rules: if: $CI_LOCAL' ([3d23883](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/3d2388336e271be770317eff712d25321adb1c0a))
- **gitlab-ci:** uninstall current package first in 'development' ([4153965](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/415396539a127466f3f7457d61174988233831ae))
- **gitlab-ci:** refactor jobs names lowercase and 'group:name' ([2017342](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/2017342edef59c83ed9eca8ff0fb307ca1564c0e))
- **gitlab-ci:** create 'gitlabci-local:preview' image with 'docker' ([ea64054](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/ea64054e5a48143a7ede80fa7cf530d51b146155))
- **gitlab-ci:** raise minimal 'gitlabci-local' version to '9.0' ([035ded9](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/035ded963fad846914cb51ab17956b2af73be6fc))
- **gitlab-ci:** fix stage for 'install' local installation job ([38e884c](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/38e884ca88e608ae812154eb301900605022219b))
- **gitlab-ci:** migrate from './setup.py' to 'python3 -m build' ([5b7eb06](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/5b7eb06ba1b5ca4d9678a9c403da6ed257fa3ad3))
- **gitlab-ci:** deprecate 'development' for 'build' + 'install' ([1c76b0a](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/1c76b0abeb1da5c77fd696d34884f40e08052034))
- **gitlab-ci:** deprecate 'dependencies' job using pip3 install ([68e3df1](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/68e3df1b47639e1abf752b30ab2d77d90ff43c69))
- **gitlab-ci:** migrate 'deploy:*' from 'dependencies:' to 'needs:' ([cf4d304](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/cf4d304628ed971369db6869c656988c36c4777f))
- **gitlab-ci:** hide 'Typings' permanent failed errors as warnings ([42da03e](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/42da03eff84cc3e6c4b8bb3d5349a6a965374df3))
- **gitlab-ci:** fail 'typings' job if latest changes raise warnings ([18e9f66](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/18e9f667bf3c5780d1670a03bcbe474aaa02449e))
- **gitlab-ci:** resolve 'typings' job for newly created sources ([906a067](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/906a06796d68e35a5a4a1033664d53080cc74393))
- **gitlab-ci:** create specific 'codestyle' image for 'prepare' jobs ([783b406](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/783b406ae62e6861e2ceda52bba89014de5e11e1))
- **gitlab-ci:** create specific 'build' image for 'build' job ([1a4e933](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/1a4e933d40161edd296520e9b3ab77e829ffdc33))
- **gitlab-ci:** create specific 'deploy' image for 'deploy' jobs ([387269a](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/387269adfec44c6b29f3efea1a0c8ce2e35db596))
- **gitlab-ci:** migrate from YAML '&/*' anchors to CI '!reference' ([82239bc](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/82239bcaa81dda425a374991f9bde8aae2a2473b))
- **gitlab-ci:** disable pip cache directory in built images ([52fcd01](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/52fcd0119d3fcd9d889e42516ee11e205b264de2))
- **gitlab-ci:** allow using 'IMAGE' variable to filter 'images' ([f21080c](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/f21080c8ee851deb1dc60efc010a5d1d83582db0))
- **gitlab-ci:** pull the previously built images first in 'images' ([97510eb](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/97510ebb041d46e8b988cc95011c658eafcdb6ac))
- **gitlab-ci:** install 'docs' and 'tests' requirements in ':preview' ([4057b93](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/4057b934836686d62d25cd695c99323deeb54bae))
- **gitlab-ci:** refactor all 'test' jobs into prebuilt images ([ab300b0](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/ab300b0c1b6fb14f2748252ff09f58b4dae6f126))
- **gitlab-ci:** add missing 'needs' sequences for 'deploy:*' jobs ([129e212](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/129e21215e6048a944120fe89c675cbc6313d130))
- **gitlab-ci:** migrate changelog commit to 'docs(changelog):' type ([c949948](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/c9499487a1a48ac37cbcc8b508155796c11f838c))
- **gitlab-ci:** create 'clean' local cleanup job with 'sudo' ([731976d](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/731976db5524d1e8ffb3960b9c92ecef74834205))
- **gitlab-ci:** ignore 'docker rmi' local failures if already in use ([41f25cd](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/41f25cd2a9218b6de24233047ff0fcf42077617c))
- **gitlab-ci:** remove 'image:' unused global declaration ([555ee7b](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/555ee7b95a245a8c138f24650127628404dabff5))
- **gitlab-ci:** disable 'typing' mypy caching with 'MYPY_CACHE_DIR' ([3894920](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/38949200338e079268bc99d6b71fd3bc3a7dfbe2))
- **gitlab-ci:** implement 'readme' local job to update README details ([1f1961c](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/1f1961c441580d3bef3cdcdfa5c616d57e11b9ec))
- **gitlab-ci:** use 'CI_DEFAULT_BRANCH' to access 'develop' branch ([f0bfc87](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/f0bfc8777d0d79f8111eced2c2abbdb05e8cfd02))
- **gitlab-ci:** change commit messages to tag name ([349e532](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/349e532ae1b30dd462e2c6bbc5f5dc9edb7fe137))
- **gitlab-ci:** migrate from 'git-chglog' to 'git-cliff' ([76bc134](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/76bc134cebe87dc48e6051e9eadc42b5b3170d2c))
- **gitlab-ci:** support docker pull and push without remote ([469a446](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/469a446eb8592199cea7ae865da797b2ff954d45))
- **gitlab-ci:** explicit 'docker' service and isolate 'DOCKER_HOST' ([6cffe85](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/6cffe85caa655cb9806e4ab347006fdcd952ca4f))
- **gitlab-ci:** use '/certs/client' TLS certificates from DinD ([0f670f3](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/0f670f394d0fe6e704b7c944738b1015b254b7f5))
- **gitlab-ci:** enable 'PYTHONUNBUFFERED' in tests to unbuffer outputs ([2f585d0](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/2f585d03982d53ac123e85933ebc3b4cbcac6ed0))
- **gitlab-ci:** fix 'coverage:*' jobs for module sources in 'src' ([7842b23](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/7842b23ffa5ffee6572943c123c1cd710ade6b48))
- **gitlab-ci:** install 'util-linux-misc' for 'more' in preview image ([35b3bcf](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/35b3bcf302f4e9fac1b623cf7607a39f6e06a333))
- **gitlab-ci:** enable 'PYTHONUNBUFFERED' in 'preview' to unbuffer outputs ([b402e70](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/b402e70b5eb83dd4439f7cc88979c89940ec9c97))
- **gitlab-ci, README, setup:** migrate to 'main' delivery branch ([1a004c1](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/1a004c169d36dbfad10eb2b1756b4d3bd3c88175))
- **gitlab-ci, mypy:** implement mypy Python linting features job ([fea265d](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/fea265dfaa2b51e86206b307041718ab7533d40c))
- **gitlab-ci, setup:** migrate to 'src' sources management ([62ec76c](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/62ec76c7e190883567fc3febf9c5fddeaea82c06))


<a name="2.1.1"></a>
## [2.1.1](https://gitlab.com/RadianDevCore/tools/pexpect-executor/compare/2.1.0...2.1.1) (2022-08-10)

### 🐛 Bug Fixes

- resolve: resolve 'pexpect' requirement for Windows ([650064f](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/650064ff99fbef7105f15c03aabd49051a929a08))

### 📚 Documentation

- changelog: regenerate release tag changes history ([9ebfde7](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/9ebfde7cc4dfcad2d99aa1cf987929df46477261))

### ⚙️ Cleanups

- gitlab-ci: restore Windows coverage job ([3a40020](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/3a40020c1bf13f081532374b31e9002a2a1244b4))
- requirements: enforce version 4.6.0 of 'gitlabci-local' ([f49700b](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/f49700bbcf400128e2803b267ce29c88a9ad6d59))
- tests: fix 'sys.exit' import from the lint warnings commit ([081f6cc](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/081f6cc56b15ead7ef5234154fd6142330bc0a50))
- tests: remove implicit engine execution test ([22498f8](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/22498f887078013a3b4a8ee64aa4c664d1695bc2))
- gitlab-ci: enforce unknown 'SUITE' filtering unknown suites ([2f39e03](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/2f39e03dbb01c1f270932f34f75f0a7df1d5c557))
- gitlab-ci: use 'tobix/pywine:3.7' for 'Coverage Windows' ([c789c7c](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/c789c7c837031d0a689001c91c4fcf5697b7c6db))
- docs: disable prompt-toolkit CPR requests outputs ([7a5f95c](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/7a5f95c84ce6fc36790bf6626ed30d24038f819e))
- tests: resolve 'colored' forced colors in CI tests ([c8194da](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/c8194dad5a23bcca79faf99fc8119a6765094eaa))


<a name="2.1.0"></a>
## [2.1.0](https://gitlab.com/RadianDevCore/tools/pexpect-executor/compare/2.0.0...2.1.0) (2022-08-01)

### ✨ Features

- run.sh: see the job name upon result for readability ([a2e14ab](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/a2e14ab1e76f36017ec97c74ec2012f713fff4b8))
- resolve #17: migrate to Python 3.10 version and images ([3c0b26b](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/3c0b26b4124d5bd8b7fe17051a6f9bda91e931fc))
- implement #16: support stripping data from outputs ([c1dd16d](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/c1dd16d908a8fa57611172c93908da03cc8784ed))

### 🐛 Bug Fixes

- resolve #18: deprecate outdated wexpect engine ([3a0e73c](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/3a0e73c0e1601823461726b4a8287e5cb6af60c3))

### 📚 Documentation

- changelog: regenerate release tag changes history ([7f94aec](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/7f94aec3192b145f61069c91cbc49b13ca3400cd))

### ⚙️ Cleanups

- vscode: cleanup deprecated Visual Studio Code extensions ([563d2d9](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/563d2d9b80c76eb52df7a917269d27299cf97d22))
- vscode: ensure Prettier formatters use single quotes only ([24f8c14](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/24f8c14eeffed9a654abf44c68f2fccb554d99dc))
- requirements: enforce version 5.6 of 'gitlab-release' ([19c87b0](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/19c87b0d756338f5d55a3b70c30309619745f3e6))
- requirements: enforce version 4.5.2 of 'gitlabci-local' ([1797d38](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/1797d389f3c033b5331227019daab8680533625e))
- sonar: declare Python versions for SonarCloud settings ([81a8431](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/81a8431748b28d16dc89cc323058786b77eb82c4))
- markdownlint: extend line lengths to 150 characters max ([1586cc0](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/1586cc0447aba5e0a96ea74d387dbc7146918982))
- setup: lint warnings on files 'open' calls ([739b422](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/739b4221df1d7af7fdeb3cecca18ef1b9cd15170))
- gitlab-ci: use the standard 'docker:dind' service image ([5fad83c](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/5fad83c1d59f2539510f0db337e725a719103e84))
- gitlab-ci: minor codestyle cleanups of requirements ([4b1bdcb](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/4b1bdcb388716f141b3bb3ce31b29732096696ae))
- gitlab-ci: run tests only on Python 3.6 (old) and 3.9 (new) ([8a2302b](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/8a2302bfd5df8a010c58d70c3693f780d33645ad))
- gitlab-ci: ensure 'Build' runs without jobs dependencies ([6538517](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/65385178967cd3ebcd7eb622e68aceb812ce3a3f))
- gitlab-ci: use 'needs' instead of 'dependencies' for tests ([dd149cd](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/dd149cd65d85143fdd5e171469797a45d88f0f63))
- gitlab-ci: always push to SonarCloud on develop / master ([d02cf77](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/d02cf77cbf70ab88db7f9a47f7df084f16407e2a))
- gitlab-ci: adapt 'prepare' and 'build' jobs to '3.9-alpine' ([678b2a6](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/678b2a6e2364760aeee370c5af7eca433460709f))
- gitlab-ci: add tests execution times with a 'time' wrapper ([3c69c57](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/3c69c578837db0254d80c810ea1d29154ff09787))
- gitlabci-local: lint warnings and Python 3.6 f-strings ([1d039e0](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/1d039e0728505f4ba08b180550ad345a4d526978))
- gitlab-ci: fix 'Coverage Windows' issues with pip and wheel ([538f582](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/538f5825b6885feceba10ada52b120346a70813b))
- docs: refresh the preview SVG presentation ([8bf1f80](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/8bf1f8050005606a3c718e2347213fc8aeb5637e))
- gitlab-ci: disable Windows coverage job for the moment ([049d1cf](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/049d1cf3a8eb22089e0ea47da726003994135c0a))


<a name="2.0.0"></a>
## [2.0.0](https://gitlab.com/RadianDevCore/tools/pexpect-executor/compare/1.2.1...2.0.0) (2020-12-27)

### ✨ Features

- implement #13: support Windows and refactor with engines ([1e160af](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/1e160af486231af1c0765455039389b0e2f35a7a))

### 🐛 Bug Fixes

- prepare #13: use 'sh' found by PATH rather than hard-coded ([a299ca2](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/a299ca29c73783463deb0b0c863fe9642c422915))
- prepare #13: define the timeout globally for wexpect support ([7de9313](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/7de9313318bbcfd3bc3d9b9db46284db5b9a134f))
- lib: avoid 'send' and 'sendcontrol' from raising 'EOF' errors ([ad5a576](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/ad5a57628b46a1e9ccd2fe21a3dacb7fe935dd90))
- prepare #13: handle 'sendcontrol' directly in 'Executor' ([9669e3e](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/9669e3eb59e6948762078e4674209c31be5af2e1))
- resolve #14: pass down the SIGINT signal to the child process ([dc90926](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/dc90926a3dd9d429120495159002c058fb901524))
- validate #13: add coverage for all Windows engines ([ce19e35](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/ce19e35620fddcd4dff2cc88a4842617f2e54367))

### 📚 Documentation

- changelog: regenerate release tag changes history ([5338fa4](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/5338fa486f44763daf539a92f952f1b2ae314ac9))

### 🧪 Test

- gitlab-ci: add 'unknown-binary' test for unknown binaries ([cf02048](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/cf02048598c5dd648db5b5581b7ddccf7a039cd9))

### ⚙️ Cleanups

- gitlab-ci: run develop pipeline upon 'CHANGELOG.md' changes ([66cb6c1](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/66cb6c174222eb31a30e487dde6174ace7adce1b))
- run: add 'run.sh' script for local development purposes ([c65cf5f](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/c65cf5fda9a3ca956ddb00488cac7de52c5f7973))
- lib: isolate the 'Executor' class to a 'lib/' folder ([b401f85](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/b401f85fb0991ec4641f48f1fe5f0352e6c78643))
- lib: use 'Platform.flush' to flush the stdout stream ([2c383db](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/2c383db2a242e3f3a1fbade85d0d627e2e7b93a7))
- vscode: ignore '.ropeproject' folder from tracked files ([45d57e5](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/45d57e5244e206c777ffb583d245f65eab1a0e6f))
- gitlab-ci: add 'SUITE' specific test command support ([f737efc](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/f737efc674c2e507fff0923218a057ad4dcdeacb))
- test: add tested environments description and install guide ([ee5ad2d](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/ee5ad2da6161cea228fffe4eefdb685574664e6b))
- gitlab-ci: add 'Coverage Windows' and merge all results ([6f71ebc](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/6f71ebc7427776c1db2e0935754f5c25379984dc))
- tests: isolate all test commands into test scripts ([0f32bcf](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/0f32bcff415ddde5d0f82023fd4d103142dc3d36))
- prepare #13: add pexpect along winpexpect for Windows tests ([29cf33f](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/29cf33fa88bac5ccaff8e0b1d0faa9c6bcf06130))


<a name="1.2.1"></a>
## [1.2.1](https://gitlab.com/RadianDevCore/tools/pexpect-executor/compare/1.2.0...1.2.1) (2020-12-22)

### ✨ Features

- implement #12: add arguments categories for readability ([db2a6d6](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/db2a6d625bbba5b72a377b26c7ec459044a9c89b))

### 📚 Documentation

- changelog: regenerate release tag changes history ([a87a8ac](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/a87a8ac4860a9f00e6dc67a3a1762838c2925f6b))

### ⚙️ Cleanups

- readme: add supported systems list of current tests ([c784fbc](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/c784fbcd1c7ebc563e5608d75a586709bd3073a6))
- cli: isolate the CLI main entrypoint to a cli/ submodule ([99b5a1b](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/99b5a1bbfbd2a4139c290225bb1fbf3cec3d09eb))


<a name="1.2.0"></a>
## [1.2.0](https://gitlab.com/RadianDevCore/tools/pexpect-executor/compare/1.1.1...1.2.0) (2020-12-22)

### ✨ Features

- prepare #11: handle prompt without hard-coded delays ([df2d8ce](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/df2d8cebc703a5c46ba7811730bead307ff545e2))
- prepare #11: override prompt delay with --delay-prompt ([c89dbc0](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/c89dbc02dce68708b26d5a6b1cf50e46eb8f320b))
- resolve #11: add --hold-prompt feature to hold the prompt ([6d3975b](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/6d3975bcba5f7b213152ed94578c9fce5872086d))

### 📚 Documentation

- changelog: regenerate release tag changes history ([5bb9724](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/5bb972479672abea8f0f4c6779f8b036e04779c0))

### ⚙️ Cleanups

- vscode: use common XML file for local VSCode coverage ([9ea9fd3](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/9ea9fd37c38c675e1898a78d0c08d791eaecd6e7))
- gitlab-ci: improve 'Coverage' scripts and unify XML paths ([2ed903b](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/2ed903b30846c719e1b99b99c5b6caa6ab70fd76))
- gitlab-ci: add stages comments headers for readability ([dea4afe](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/dea4afe0ef61db390e2b7ea7a92fd340625c71eb))
- gitlab-ci: use pip3 instead of pip in the tests template ([9c0b675](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/9c0b675b95b2934781f3481d570005ca960876ef))
- setup: minor comment codestyle cleanup ([9bbe427](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/9bbe427daefecf1dca148a584c6c49041bc70be3))
- docs: refactor the 'Preview' job into a 'termtosvg' job ([a41e45b](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/a41e45b3e625d2f7e91854aa6e4a0e1656e71c33))


<a name="1.1.1"></a>
## [1.1.1](https://gitlab.com/RadianDevCore/tools/pexpect-executor/compare/1.1.0...1.1.1) (2020-12-15)

### 🐛 Bug Fixes

- resolve #10: handle Ctrl+C interruption in finish ([29fb85f](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/29fb85f67b43d6c3cf98aff8f64c0a8f67bf5c02))
- resolve #10: ensure actions checks for the executor ([b404381](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/b404381d38c410944969f9c07a5fc643818a3f74))

### 📚 Documentation

- changelog: regenerate release tag changes history ([117138e](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/117138e2bf281990fbc5a47d771ce0b447622165))

### ⚙️ Cleanups

- commands: cleanup unused code and add an empty command test ([aef699f](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/aef699f17d76c24ee060751f043c4a4353aa2ad1))


<a name="1.1.0"></a>
## [1.1.0](https://gitlab.com/RadianDevCore/tools/pexpect-executor/compare/1.0.1...1.1.0) (2020-12-14)

### ✨ Features

- implement #8: add EXECUTOR_{HOST,TOOL} environment variables ([ea48308](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/ea48308ddceec40d5f2bb522b853b52e63b6f04d))
- implement #9: use 'colored' and improve prompt colors ([122b4bf](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/122b4bf76970b6568ce5cbc40655abac75dd79ec))

### 🐛 Bug Fixes

- resolve #7: preserve command arguments containing spaces ([be1d222](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/be1d2223604bc6bd4ad95d5d83df156da9da71a5))

### 📚 Documentation

- readme: add missing --workdir metadata variable ([f5780c8](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/f5780c833aca6a1d642d7c9f62305e15dce6fb2e))
- readme: add missing modules dependencies and references ([08daac0](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/08daac032753ec6c25199e0e0682d023a60861dd))
- changelog: regenerate release tag changes history ([63084f4](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/63084f4de5551b6341d28b03331d4b4c2e717152))

### ⚙️ Cleanups

- changelog: add a cleanup option to hide changelog commits ([3b2c1a4](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/3b2c1a4145a704ac90995928e9428742d27f16ca))
- changelog: configure groups titles detailed map for chglog ([74c5b55](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/74c5b55b0ee70782317566ba3127c1a6458314fe))
- vscode: disable chords terminal features to allow Ctrl+K ([64ea15e](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/64ea15e7a059f41d855fde131be73d471d5966f8))
- gitlab-ci: use updated 'docker:19-dind' image for 19.03.14 ([3cb1cfb](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/3cb1cfb34b4e93575bee2d47a7ace0aae155b988))


<a name="1.0.1"></a>
## [1.0.1](https://gitlab.com/RadianDevCore/tools/pexpect-executor/compare/1.0.0...1.0.1) (2020-12-13)

### 🐛 Bug Fixes

- resolve #6: ensure the input delays are float values ([52c5c7f](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/52c5c7f10da2850a58504bae0b9b5c600e34c910))

### 📚 Documentation

- changelog: regenerate release tag changes history ([8eb21f9](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/8eb21f906338fa2cd069b35100483f15c90080ab))


<a name="1.0.0"></a>
## [1.0.0](https://gitlab.com/RadianDevCore/tools/pexpect-executor/compare/0.0.1...1.0.0) (2020-12-13)

### ✨ Features

- implement #2: add delay values configurations ([3c781de](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/3c781de005b894618ae0038cd528f00a3126956f))
- implement #3: add Ctrl+key press feature and LEFT/RIGHT keys ([9d9e415](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/9d9e415546ffb4996a5e474a5c1fedbdd630d429))
- implement #4: handle forced finish and wait output ([d16235c](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/d16235c8f90207040a6d4c851b0be69eacca74ea))
- implement #1: create a command line wrapper to run executor ([c173c6d](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/c173c6d159777ab597e6d0c32849a12a316d942c))

### 🐛 Bug Fixes

- resolve #5: enforce against missing child or empty command ([e596f59](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/e596f5911f8d79f91dd48da8a186179ad54b2e35))
- finish #2: resolve initialization delay to read first output ([e10ba7b](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/e10ba7b30253c9e1d5e3f76e43c5b8e8325ae7f9))

### 📚 Documentation

- changelog: regenerate release tag changes history ([594207c](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/594207c52b9995f6042bf491b18191b9fe80aeb0))

### ⚙️ Cleanups

- vscode: migrate to 'brainfit.vscode-coverage-highlighter' ([836e0ca](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/836e0ca47d70c717b58b667ca9cd04a8a0fb629e))
- vscode: exclude intermediate files from the project view ([774ccd5](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/774ccd57376fd49e970ed82693a61490303b50be))
- gitlab-ci: resolve 'SonarCloud' changes rules on develop ([a54059b](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/a54059beefc265b6ecda9e1f0147211ad596dbc9))
- gitlab-ci: isolate coverage database and quiet requirements ([2c6b35c](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/2c6b35c9b2a2101da1d995329ba472456f95d9be))
- gitlab-ci: run coverage and SonarCloud upon tests/ changes ([37abaf3](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/37abaf36fa150b66170023d44332fa720fbcd096))
- gitlab-ci: unify coverage reports and common scripts ([62b02e6](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/62b02e69a72f922ae55dbbceede38bfffb97428b))
- finish #2: refresh the README examples ([0634a82](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/0634a824ff4e194133b406b6ab4db87fe840d150))
- gitlab-ci: ignore 'too-many-arguments' in Lint checks ([4286952](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/4286952b747003511e19fa3e19494beed8277edb))
- finish #1: add unit tests for the CLI wrapper ([3674c90](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/3674c90792e534ad9993930ccc356a9738f521ba))


<a name="0.0.1"></a>
## [0.0.1](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commits/0.0.1) (2020-12-12)

### 📚 Documentation

- changelog: regenerate release tag changes history ([afc871b](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/afc871b46c92ee802d8b8973de82bcc14ec39c63))

### Pexpect-executor

- migrate implementation out of gitlabci-local ([e524262](https://gitlab.com/RadianDevCore/tools/pexpect-executor/commit/e524262cad98eacdcb7ea79cb02c6fbbccc99b56))


