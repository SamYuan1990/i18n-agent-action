## Why we have this

It was discussed on KCD 2025 BeiJing, Community Over Code 2025 China and we finally dicede to make an agent to handle i18n works for community.
As for me, I can't parallel in [https://github.com/sustainable-computing-io/kepler-doc/issues/175](https://github.com/sustainable-computing-io/kepler-doc/issues/175) and Community Over Code 2025's session.

## In scope and not in scope, and how it works

> Don't want to rebuild the wheel.

- Trigger is not in scope
  - leave to manual for full refresh or diff action
  - model api and model endpoint
  > people can select any LLM service with openAI API?
  - config entry point
  > We need to know the default language and what languages are the target, it's in the config file.

--- scope ---

- Phase one: from configuration file

> Sam at 2025 July: I don't want LLM to scan the project, as token cost or it may wrong. Just ask document maintainer to give the i18n configuration file, the manual point to configuration file will be 100% correct to i18n config.

- language scope, how to get language scope?
  - = consume config files to get language list.
  - = default language - existing language(a file diff)

- save result to the specific file

> Sam at 2025 July: after we have translation scope, we also need to have naming rules from configuration files.(or maybe ask LLM to notice that)

-- end of here: get a list for source file, translate target, language.
> Sam at 2025 July: as result of this phase, we need to have a clear scope for all the tasks.

-- Phase two, A for loop here to translate

- Translate ask LLM for help
  - how to get a glossary for content mapping?
  - Gaps?(or just refresh all)

> Sam at 2025 July: to be specific.

--- not in scope ---

- create PR leave to PR Action

> Don't want to rebuild the wheel. as there are PR actions already to open PR for change.
