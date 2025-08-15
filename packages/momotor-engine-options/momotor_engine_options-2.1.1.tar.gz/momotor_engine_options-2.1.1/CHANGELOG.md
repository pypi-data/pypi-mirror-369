# CHANGELOG


## v2.1.1 (2025-08-15)

### Bug Fixes

- Allow `None` for task number iteration functions
  ([`995a28a`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/995a28ae0b3bc799e28e8219359c622feaa1ab9b))

### Chores

- Update pytest options
  ([`3323338`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/3323338ae2f6fe6bec3080d8a66931246d09cc5c))

### Refactoring

- Update typing
  ([`02f08cb`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/02f08cb52618f334ff9cba165391f982c34fb1bb))


## v2.1.0 (2024-08-26)

### Bug Fixes

- :momotor:option: references do not work
  ([`732de7d`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/732de7de1be4b54899689fd3156eb90d30ab9a99))

- Show control (e.g. newline) characters in value strings
  ([`53f11ba`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/53f11ba03e9176569bb099ed40315cb9d29f77fa))

### Features

- Handle step context for options
  ([`023a3a4`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/023a3a4c0d826b4d81dc3f3b5c2f7c71735463b1))


## v2.0.3 (2024-07-04)

### Bug Fixes

- Correct separator string
  ([`5a0be3a`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/5a0be3a3fada65105303ee9541423058c0d758d8))

- Os.path.realpath strict argument requires Python 3.10+
  ([`68eecdd`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/68eecdd1f22d1cfc701160a8e0f3f53db632c503))

- Use short option name if it's in the default domain
  ([`67294d1`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/67294d11ca32b178643b2882304bec8a2c577326))


## v2.0.2 (2024-04-25)

### Bug Fixes

- Do not add an empty or None label property
  ([`2f887e7`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/2f887e750499ccc662b2dd00ad9f89d600f5d0df))


## v2.0.1 (2024-04-16)

### Bug Fixes

- Update dependencies
  ([`1b4261a`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/1b4261a04486ff6174ae9cd1b7f3109b4f2684ed))


## v2.0.0 (2024-04-15)


## v1.2.0 (2023-10-26)

### Chores

- Show exact reference used in exception message
  ([`177fed1`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/177fed1379073bab8738a9b3785d1d0be7966ef0))

### Features

- Change `get_scheduler_tools_option` to include results bundle in option resolution, so references
  to step results can be used
  ([`39e2183`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/39e218353d7eea2297b992e273bdc4550b3ba14b))


## v2.0.0-rc.11 (2024-03-19)

### Features

- Convert to PEP420 namespace packages
  ([`1b01285`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/1b01285620e39f7882e5a68590afdc5e2ee2e1b5))

requires all other momotor.* packages to be PEP420 too

BREAKING CHANGE: convert to PEP420 namespace packages

### Refactoring

- Replace all deprecated uses from typing (PEP-0585)
  ([`00021e8`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/00021e8ea1111d2112e611bd93975082678997d1))

### Breaking Changes

- Convert to PEP420 namespace packages


## v2.0.0-rc.10 (2024-03-04)

### Features

- Extend `document_option_definition` to document step options
  ([`83bbd22`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/83bbd22735b19f60c6ee7d2165dd0bc1e3f86876))

### Refactoring

- Update type hints for Python 3.9
  ([`9705bb8`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/9705bb832c19673b6fd8f0016ca0fc342bced1cf))


## v2.0.0-rc.9 (2024-01-16)

### Bug Fixes

- Allow comparing of OptionNameDomain with other types
  ([`9cb473b`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/9cb473b9841614fe4a64f3dca9ac8629e706cadc))

- Docutils is an optional dependency
  ([`1942882`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/1942882b2762b9cb14c78ff28e29e94c0b37093e))

### Features

- Add Sphinx extension to handle external references to local package
  ([`297382e`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/297382e142841a1211c2452261e12fdbcd1e22c2))

BREAKING CHANGE: moved `momotor.options.sphinx_ext` to `momotor.options.sphinx.option`

- Remove deprecated interface of get_scheduler_tools_option()
  ([`130078d`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/130078d9c1d6d97397918565f71e3a7bbb1b41df))

BREAKING CHANGE: deprecated interface of get_scheduler_tools_option() removed

### Breaking Changes

- Moved `momotor.options.sphinx_ext` to `momotor.options.sphinx.option`


## v2.0.0-rc.8 (2024-01-12)

### Bug Fixes

- Always include domain in option name ids
  ([`71fdf62`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/71fdf62552c86f6886875514856f2e6c3aaf2b4d))

- Change rendering of option attributes
  ([`a301d2d`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/a301d2d44ba9fd7004b6a24630c41ea7241a1a98))

- Correct toc entries
  ([`0ef4f2f`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/0ef4f2fa049d4e60f5f46a4ad6281988cff41bf2))

### Features

- Add `annotate_docstring`
  ([`3033245`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/3033245069fe1ef9b56ffe67d14bfa62fdb2a52d))

- Make it possible to xref a local option in the same checklet
  ([`a3ee72e`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/a3ee72e60c639713a07ac3560f56e5e9d95e50d8))

### Refactoring

- Remove __all__ from __init__
  ([`d55e4e4`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/d55e4e49c6b46d35e5540e7fca6ccf839705fb6c))


## v2.0.0-rc.7 (2024-01-09)


## v2.0.0-rc.6 (2024-01-09)

### Bug Fixes

- Correct xref anchors
  ([`e22d78c`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/e22d78cb5cccc2d876680b1e2ea9418272f3c5a6))

- Iterate over all references
  ([`156cf7d`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/156cf7d571c0f87741bd644b2a8d06164d53193d))

### Features

- Add 'canonical' option location link
  ([`f35bbf4`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/f35bbf4a0e8e9fc5d171e0044448ce0dae0773cf))

- Extract and document task id placeholder replacement into a separate function that can be used by
  checklet base
  ([`ad6a189`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/ad6a189f2b4b5dbbd472c11d5b010828d52d229c))


## v2.0.0-rc.5 (2023-12-18)

### Features

- Add options to toc and index
  ([`6814583`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/68145835c0a61d0b27db2edd69fa4cc39c17cbab))


## v2.0.0-rc.4 (2023-12-07)

### Features

- Extend OptionNameDomain
  ([`bbbf44d`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/bbbf44de3669fe41ae5fb6e8c30cd5aac2759c15))

- Update Sphinx extension to use auto documenter
  ([`cb000e1`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/cb000e1c65b81100424cc68957a2980a2ee8e71f))

### Refactoring

- Modernize type annotations for Python 3.9+
  ([`420ec5b`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/420ec5bac5af8bb461b5931349d0152e1003b9fe))


## v2.0.0-rc.3 (2023-11-23)

### Bug Fixes

- Revert renaming of option definition variables
  ([`98158eb`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/98158ebff18cc4e625cb295fb3c11784c58b5cd6))

partially reverts c6ae56a7277f55adde1d3f24304995ed29e0a124

### Chores

- Show exact reference used in exception message
  ([`e38164b`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/e38164b11a420a2285e1cd4c96482bbe89fb2e24))

(cherry picked from commit 177fed1379073bab8738a9b3785d1d0be7966ef0)

### Features

- Change `get_scheduler_tools_option` to include results bundle in option resolution, so references
  to step results can be used
  ([`ca7a0ad`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/ca7a0add9b0931bbaacc64206a492f06eaf8f839))

(cherry picked from commit 39e218353d7eea2297b992e273bdc4550b3ba14b)


## v2.0.0-rc.2 (2023-10-16)

### Bug Fixes

- Correct intersphinx reference
  ([`2953268`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/29532680d40366a7e66f3bb6ece732d22d2917a3))

### Features

- Extract method to generate option name and ref
  ([`b7b5021`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/b7b5021d2ad222a787bc20296f67a57cbb027315))


## v2.0.0-rc.1 (2023-10-12)

### Bug Fixes

- Ignore sphinx_ext.py if docutils or Sphinx are not available
  ([`28f5c64`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/28f5c64a754dca19aeec49738c2d5e41cb2b0c83))

### Features

- Add Sphinx extension to document OptionDefinitions
  ([`c6ae56a`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/c6ae56a7277f55adde1d3f24304995ed29e0a124))

- Upgrade momotor-bundles dependency to ~8.0
  ([`4505edc`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/4505edceceb200eb43f32bdb3c117d2309a6fdad))

* `CircularDependencies` and `InvalidDependencies` exceptions moved from momotor-bundles to this
  package

BREAKING CHANGE: minimum required Python version bumped to 3.9


## v1.1.1 (2023-08-29)


## v1.1.0 (2023-08-29)

### Bug Fixes

- Emulate LabelOptionMixin's handling of the label option when preflight causes step to not execute
  ([`6383900`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/63839005e2e5ea4d401330fbc25c4e3e28ff94e9))

- Regression: preflight option selector placeholders are not expanded
  ([`bdfa8c0`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/bdfa8c09ef7544342e4aaa451ce2bed7a834a207))

### Features

- Add json style preflight status
  ([`a346c6d`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/a346c6d09905b92f61cbaaae39795e1d2aaddd43))

### Testing

- Update to latest Pytest
  ([`2b2bb42`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/2b2bb425e0af16a6151d816933bcb678e010f1a7))


## v1.0.0 (2023-07-06)

### Chores

- Update supported Python versions
  ([`e1a3d05`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/e1a3d05abcfbaaec61b24ad21e94e599e1e869c3))

BREAKING CHANGE: Dropped Python 3.7 support

### Features

- Support sub versions (dashed suffixes) in tool versions, to support Anaconda 2023.03-1
  ([`aee2c3f`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/aee2c3f1d266b78deb2c2a8bb20c756cb382d361))

### Breaking Changes

- Dropped Python 3.7 support


## v0.10.1 (2023-06-19)

### Bug Fixes

- Some error messages were incomplete/cryptic
  ([`3b37a8c`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/3b37a8c1a2998e68b0661ff3999d4ab41a063571))


## v0.10.0 (2022-11-15)

### Features

- Add 'pass-hidden' and 'fail-hidden' preflight actions
  ([`c749a05`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/c749a0560083ee6395ccdb829714626ff1f67796))


## v0.9.1 (2022-10-27)

### Bug Fixes

- Strip leading and trailing whitespace from selectors and references
  ([`929d233`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/929d23349700132234848921ed19de1f16628374))

### Testing

- Update doctest
  ([`271174c`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/271174c31817d30434bc6a1e83e01efa45f99e27))


## v0.9.0 (2022-10-21)

### Chores

- Clean up tests
  ([`07b254c`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/07b254ce97e10f0f86ac91c4bf2a4e772d670bde))

- Clearer error message
  ([`3b81567`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/3b81567c15e1c95bda3811a0dc5d617aa6f3e8b8))

### Features

- Restore `!` selector operator
  ([`d4581ba`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/d4581ba2bbb5356e12c639597396eafe76d0acf4))


## v0.8.0 (2022-10-06)

### Chores

- Update version pins
  ([`508c7d9`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/508c7d994d3ce7e7b366f8a2bc635e4fa0e5679d))

### Features

- Add optional dimensions to `tasks@scheduler` option
  ([`9a4c768`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/9a4c7684392c10b9dfbc43d4525335ca3d2e1b60))


## v0.7.0 (2022-07-19)

### Features

- Add key-value list parser
  ([`825d5ac`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/825d5ac277b3d687a4a2b0d1190a6dfdc047b307))


## v0.6.0 (2022-07-07)

### Bug Fixes

- Expand task-id placeholders in references
  ([`545a619`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/545a619b495e7ab0f9c12d9ee4b9ab41b77d1c76))

- Handle tool options provided as child content
  ([`1a99ffb`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/1a99ffbbcbafdaba7e2451dec8e5bf46ee893e6a))

- Relax task reference parsing even more. the initial dot is now not required anymore. the $ and
  internal operators can be escaped to ignore them
  ([`f353e7d`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/f353e7d6d52f772f76c326611bdbdb5513b8113b))

- Relax task reference parsing, allowing trailing text immediately after the references without a
  dot as seperator
  ([`829b40c`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/829b40cee42ad376d4d000d3a3f0f780953eac94))

- Support placeholders in tool options
  ([`796f3ce`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/796f3ce75ebc404e08f86234154270215357c3fb))

### Features

- Add `empty_values` argument to `convert_intlist`
  ([`6be2ea1`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/6be2ea14c10d60fb2967424fe691df28eb95ed5f))

- Add `sumf` and `sumr` modifiers
  ([`533f0cb`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/533f0cb7033cc2ff5d4e005852bd75b259ae7923))

- Add convert.convert_intlist
  ([`9a071c8`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/9a071c8816ea8e913baac322ab409bafe8fb7bd8))

- Update ToolName.factory to accept a deconstructed tool base name and versions list
  ([`7d1b8e2`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/7d1b8e283d9c99bd3ab5effc03f9d0692fbb7267))


## v0.5.0 (2022-04-08)

### Bug Fixes

- Correct option type usage and handling
  ([`2a0a537`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/2a0a537a2d2dfdab43fa3ab49c6c355c41170311))

- Use option types as defined by the momotor-bundles package
  ([`e53b4c3`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/e53b4c3fddc5dd03ea18d8d99a87c19d3012c50f))

### Features

- Add duration and size conversion methods
  ([`424815f`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/424815fcc9c57d2e62dbd79e017e5e039a660a62))


## v0.4.0 (2022-04-04)

### Features

- Add OptionDefinition.deprecated
  ([`9a98031`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/9a98031723833fc5717027b56d890f47f3bd0e76))

(redo from commit 5cbfdf4834ad5bafc9c91972371f5978ee2c0a13 to fix commit message)


## v0.3.0 (2022-03-14)

### Bug Fixes

- Add more unit tests for cases with defaults
  ([`fd425a2`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/fd425a211f4d34bbc10b9a1d84204d5f4563ca26))

- Add SimpleVersion.__str__ for consistency with ToolName
  ([`0b37ae0`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/0b37ae0453a937cbed346ae7a7769ed1b78f94e4))

- Consistent argument naming
  ([`b0f8af5`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/b0f8af5cf430acbdc490309159f65d6b5cb73e6b))

- Convert tool_info.name to str
  ([`ba157aa`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/ba157aa1ea007c9a4ce324542c839bd6a7475ee3))

- Correct handling of version directories
  ([`785d674`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/785d67403012facd45c5483d59d8a54a7b66cf03))

- Correctly handle symlinks in registry
  ([`3b70e30`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/3b70e30860a3f7c5c1cbf5a6b11338e0c45f7d0a))

- Hide hidden fields from repr
  ([`cddbd6f`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/cddbd6fc8cac215343cd39001d3e3bc1f7f7ec27))

- Make Tool.name the resolved name, add Tool.__hash__
  ([`3d084a5`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/3d084a5bc97f5b51ca4dabd9ae0ad147075f3119))

- Match_tool should return the exact value from tools argument
  ([`ed324ab`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/ed324abf0dc848485e54bdc40655c1a5e6d4ae20))

- Move NO_DEFAULT into OptionDefinition
  ([`7382692`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/73826926ea91293d249b7cef8b2491fba12903ea))

- Set fixed location for tools domain options, use ToolName.SEPARATOR constant
  ([`d7db33a`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/d7db33a97e6f0020c9cc7c7aee8a806d5f330945))

- Toolname and SimpleVersion hash should be based on version(s)
  ([`69eae79`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/69eae79300e808f052842a807abb8e9c207800ee))

- Toolversion.is_partial should also return True if either version is DEFAULT
  ([`fd382f8`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/fd382f8d6ddc20f135d258743c1049bb1a588aa8))

- Unit test
  ([`7755c6e`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/7755c6e24bd0589d4f9ad7967d77c4fb6346cda4))

- Unit tests
  ([`b2a2871`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/b2a28712077097c0ff74c15edfbaad33f65241e9))

- Use `_default` as default tool version or name
  ([`cc551de`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/cc551de6a5aecfffeaee3404d983d95dedf9f9fb))

- Various fixes, cleanups and changes
  ([`273a1ea`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/273a1ea7ee741dcd1de266328e1a2e2b9adcbf4f))

- When numeric versions and named versions are mixed, the numeric versions should be preferred over
  named versions
  ([`b352fce`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/b352fce768044ef910df9c1b27e58fccf6c57b67))

### Chores

- Debug logging change
  ([`a2b4dc6`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/a2b4dc643811f4ef92940888b39340c37f442bbd))

- More test cases
  ([`35fc029`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/35fc0297615fb90aba69492589a2b14dd3905bc8))

### Features

- Add function to match tool from a list of alternatives
  ([`1c25d2d`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/1c25d2d95100f2a541fb1a931ac9b5a2be8342e2))

- Add functions to access tool registry
  ([`935d0df`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/935d0dfc9184a9fd6fa90b9469d104b4dad1b2d7))

- Add momotor.options.domain.scheduler.tools.get_scheduler_tools_option
  ([`3f16a99`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/3f16a9983a59d85fec01d326de8b8b84c9adf8a7))

- Add ToolOptionDefinition
  ([`ab5f387`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/ab5f387b64c71fb6e853c0532b98a3baf73b65ef))

- Add ToolRequirements type alias, cleanup imports
  ([`5012876`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/50128762927fae7413f0658feb92c3b12841ac61))

- Added `match_tool_requirements`. Also refactored types
  ([`2dd834b`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/2dd834be877c596ea79f7ee68ae55b43d67f07c9))

- Allow multiple version preferences to be supplied in the tools option
  ([`4f4f6ba`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/4f4f6ba55bbf284213ed502bbfa9a4fc3c05ab9b))

- Allow parts of tool name to be a wildcard when resolving, correctly merge versions in multiple
  registries
  ([`1064f69`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/1064f69247445dc87f77e46cc543f355f4e3eb38))

### Refactoring

- Clean up and refactoring
  ([`8fcf186`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/8fcf18649d366ae2a96636024e283bc1631868d8))

- Make SimpleVersion and ToolName dataclasses, move some module level constants to these classes
  ([`3a609ea`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/3a609eab22d80d9cceff68bf4ee84804e2459d63))

- Merge tool name and SimpleVersionGroup
  ([`76ba79e`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/76ba79efd21a055ae07e65e0da9a0fc00d310d21))

- Split registry.py into multiple files
  ([`ee7d28d`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/ee7d28d112d4546fb832441a27048414282fe3c2))

### Testing

- Update unit tests
  ([`a1c8d94`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/a1c8d94a1b27d88044d02c6e2088fb4f4d62dacd))


## v0.2.3 (2022-01-24)

### Bug Fixes

- Replace_placeholders() should accept any non-string value argument
  ([`0035b68`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/0035b6854bbd37decdbabf25c2132eace308cc27))


## v0.2.2 (2022-01-21)


## v0.2.1 (2022-01-18)

### Bug Fixes

- Add unittests for all combiner modifiers, fix issues with the combiner modifiers
  ([`adc6475`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/adc6475dfe54d85871b554d6b3da3aba433c61c4))

- Include options from step in preflight result
  ([`ba5070b`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/ba5070b8335732ab8849e5afc6eeafe7bc09134f))

- Use 'skip-error' action as default error action
  ([`c98e3da`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/c98e3da587ecaed17c935e21f11800f34787031c))


## v0.2.0 (2022-01-18)

### Bug Fixes

- Add logging
  ([`0369311`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/0369311bb5c94d00c8b139d09aa958b35476d6a3))

- Change 'no'/'none' into 'notall'/'notany', implement same for value references
  ([`0599591`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/05995916a914e68d02080458e9166e7ade1f9ef6))

- Correctly handle option domain defaults
  ([`11e3ca8`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/11e3ca85192802e6a472d6fa265e167eeaca19d0))

- Handle ids with wildcards in references (closes #7)
  ([`9370fe8`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/9370fe8dffd8e112bfdfc22a8de7f33a50443ad5))

- Handle invalid selectors
  ([`e136e41`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/e136e410b699bed4f4c9b55528b9284aba99469a))

- Make %not an alias for %notany
  ([`0884717`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/088471781b977985976019b2baaa31d7ee297fd3))

- Preflight option can have mod
  ([`208ac07`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/208ac079b28c29773fe6403c81db2a66915037c8))

### Chores

- Update version pin to use release version
  ([`b7afd8f`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/b7afd8fd642dc18e074e51ac9d487eb8d9f2da03))

### Features

- Added 'no' match modifier, removed '!' operator
  ([`39f6f12`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/39f6f1229a881d27688a9684de75325cbf3317be))

- Allow multiple providers in references (close #9)
  ([`9ae0b1a`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/9ae0b1afeec9c250d828b4e917c8618091d1b343))


## v0.1.0 (2022-01-17)

### Bug Fixes

- Add 'source' property to preflight result bundle
  ([`a6086aa`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/a6086aa9a5c606dd975ab7e721749fb478fe51a9))

- Change 'preflight' boolean property into 'preflight-trigger'
  ([`7596519`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/7596519db448157dc3bac6f13f5816a51e263f18))

- Change default pre-flight error action to 'error'
  ([`ea21419`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/ea21419a31f49e919961fa95afec8213aeb8a605))

- Conditions as part of selectors can contain '#'
  ([`9c47283`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/9c47283eb75e63b5465bc51e9fe27b8d9e8b04c9))

- Correct providers for tasks@scheduler value
  ([`5a5c803`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/5a5c8034b563c282641efeddf307eff8535b1997))

- File-references class part is default
  ([`c9095d0`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/c9095d06b03e49097b1d58de20544622331b8ea3))

- Filter invalid refs
  ([`217194b`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/217194b874df5c1dcff785a00ad22b20c426df57))

- For 'sum', 'min' and 'max' modifier, cast items to numbers
  ([`77fd72e`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/77fd72ec052a99d6f4bfb7c663a8d5818a9e0411))

- Generate correct subdomains and collect all options for preflight option
  ([`2a9bfeb`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/2a9bfeb681e21e3bf09d3a1a33557210a5e70675))

- Make VALID_LOCATIONS a set
  ([`70b2dd6`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/70b2dd692520d1795c951aad24a4b0f4a4e692df))

- Match_by_selector should always return False if no objects match
  ([`131bd6b`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/131bd6bf5f2da1766333bbff7f3f05bef012f8d1))

- Only raise InvalidDependencies for explicit dependencies, not for wildcard or placeholder ones
  ([`50f54ac`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/50f54acc44899f0d3987a3585cca3a61be302651))

- Properly document and validate required OptionDefinition.location and OptionDefinition.domain
  attributes
  ([`ecb287e`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/ecb287e6af5143b15ded809974aea03331a52d21))

- Properly document and validate required OptionDefinition.location and OptionDefinition.domain
  attributes
  ([`14ea4e0`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/14ea4e0679dc18035e4845ffcf2f6858320dfe90))

- Refs have multiple id's, but only a single class/name part; return all elements even if there's no
  match (needed for match selector)
  ([`17c47fa`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/17c47fa7ae03bfe9644bfc5cd0025a002b20cea8))

- Remove mod parsing from `parse_selector`
  ([`3b975fe`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/3b975fef5ae0e0fa96e35b4caee81c739983db95))

- Remove unused function
  ([`46762aa`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/46762aa0b93a4101492f6ea12db48bbbb3ac10c1))

- Restore tests for select_by_XXX_reference
  ([`d21d72b`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/d21d72bd5c959d38811b6d8cfab6e4346f7c5319))

- Swap "?" and (no oper) operations
  ([`92523b9`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/92523b92ea44596c46b82261385ec57b3c704fed))

- With task numbers available, step option is no longer needed
  ([`a5b898f`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/a5b898fcad77e5e81f7822fa1660d62dbede978f))

### Chores

- Add missing doctest-plus requirement
  ([`b0ba335`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/b0ba33508f17810ef8909fed37ee91ff903363ff))

- Add missing pytest.ini
  ([`2adc01f`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/2adc01f06aa41b592f09cf06730b133bb4d8e17d))

- Add missing shell scripts and docs placeholder
  ([`83a50de`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/83a50de4d10507a37cffdf80591c6b92bf9151fb))

- Drop old parsers
  ([`98ba797`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/98ba797449dc75282ceb770c4b1cb94cfc3f9e74))

- Reorder imports
  ([`0bdd5d2`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/0bdd5d2f329c33c52ba63e52c1af07abc4cbbcbb))

- Update version pins
  ([`5fcc495`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/5fcc495dda88db95fb6f113d99a49f5b70342edb))

### Features

- Add '!' and '!=' operations since there is no more "not-prop" type
  ([`cc3b698`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/cc3b69836ffa3e50138e68214ad7972310cc51d0))

- Add 'always' preflight option action
  ([`5459dcb`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/5459dcbbc12d2c60239a3b028f97f2adcbf8d832))

- Add `result` reference type
  ([`ac52431`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/ac52431385fb98c0cae276470396a8df2f656cbb))

- Add `value_processor` to apply_template
  ([`3dabf78`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/3dabf78e4bc82139e99f0aac694a5a8778184f12))

- Add argument to change default modifier for resolve_value_reference
  ([`59bbe20`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/59bbe20b94c582c432dc83e081487cde2f9ea685))

- Add filter_files.ifilter_files()
  ([`b369b1c`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/b369b1c80bcef29e135f47eae5571106caef95cf))

- Add generalized parser and resolvers for outcome/property/file/option references
  ([`03a6dc1`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/03a6dc1df9b18abea51d165cafddf70ee1019257))

- Add new selector methods
  ([`0d30ac5`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/0d30ac5005124b3e3c6324b112bb0e733f481991))

- Add task-number expansion
  ([`16f6442`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/16f64425e5e44243b42e013f16107065e01fe5d4))

- Add template parser
  ([`cd7c1ea`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/cd7c1ea1896e121aaf8d9202a2cb692c8e9be8d7))

- Allow OptionDefinition.name to be an OptionNameDomain object
  ([`eb9da99`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/eb9da99dfc82383bf720b0cce1f8f3252355aa48))

- Change reference resolver to return both the containing element and the resolved objects
  ([`9f8f054`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/9f8f05452e853f7a7d8135fda8db6d5b0d3e1c83))

- Extend condition parser to check file counts
  ([`9b96339`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/9b963399a69c83bbcf90eb1924496b6860eb60e9))

- Generate default option subdomains (closes #7)
  ([`8e39f09`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/8e39f0954b5c3b982b9a651dca2632d2d9cbf28a))

- Make OptionsProviders more generic and also use it for the parsers
  ([`f03bd77`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/f03bd77778155d27de43025c4abe6d680799dc7c))

- Rename 'step' domain to 'scheduler', add 'preflight' scheduler option
  ([`a5c8318`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/a5c831832d6d34abe4fe08f21c9d4792cc76c293))

- Replace placeholders in tasks@scheduler option
  ([`72798b9`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/72798b93afe10488e0c60e87d82e0b940966153b))

- Restore the select_by_XXX_reference methods
  ([`e7ce22b`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/e7ce22bf3d89d2f50e659b6366fe19681de751da))

- Restored filter_result_query function
  ([`e20003a`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/e20003af48e9313ea170a1f1d72bf3c691c9d2b1))

### Refactoring

- Move apply_task_number to task_id module
  ([`15e22ee`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/15e22ee93cc47c8633ddeb273200a68a3d391af1))

- Rename 'templates' to 'placeholders'
  ([`b229ad0`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/b229ad0bb6cc090809beab661478e375073f872b))

- Renaming, reorganizing and refactoring
  ([`60b48b9`](https://gitlab.tue.nl/momotor/engine-py3/momotor-engine-options/-/commit/60b48b959038ac177b2f7f054b19fd303f6aeae1))


## v0.0.0 (2021-12-09)
