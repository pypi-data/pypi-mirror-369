![](https://github.com/hasii2011/code-ally-basic/blob/master/developer/agpl-license-web-badge-version-2-256x48.png "AGPL")
[![CircleCI](https://dl.circleci.com/status-badge/img/gh/hasii2011/code-ally-advanced/tree/master.svg?style=shield)](https://dl.circleci.com/status-badge/redirect/gh/hasii2011/code-ally-advanced/tree/master)
[![PyPI version](https://badge.fury.io/py/codeallyadvanced.svg)](https://badge.fury.io/py/codeallyadvanced)

Host common UI artifacts for various projects I am developing

___
Common wxPython UI artifacts for various projects I am developing

* Dimensions Control
* Position Control
* MinMax Control
* Directory Selector

![SpinnerWidgets](./developer/SpinnerWidgets.png)

* DialSelector

    ![DialSelector](./developer/DialSelector.png)

Written by <a href="mailto:email@humberto.a.sanchez.ii@gmail.com?subject=Hello Humberto">Humberto A. Sanchez II</a>  (C) 2025

## Note
For all kinds of problems, requests, enhancements, bug reports, etc., drop me an e-mail.

## Developer Notes
This project uses [buildlackey](https://github.com/hasii2011/buildlackey) for day-to-day development builds

Also notice that this project does not include a `requirements.txt` file.  All dependencies are listed in the `pyproject.toml` file.

#### Install the main project dependencies

```bash
pip install .
```

#### Install the test dependencies

```bash
pip install .[test]
```

#### Install the deploy dependencies

```bash
pip install .[deploy]
```

Normally, not needed because the project uses a GitHub workflow that automatically deploys releases

---

![](https://github.com/hasii2011/code-ally-basic/blob/master/developer/SillyGitHub.png)

== I am using GitHub under protest ==

This project is currently hosted on GitHub.  

I urge you to read about the [Give up GitHub](https://GiveUpGitHub.org) campaign from [the Software Freedom Conservancy](https://sfconservancy.org).

While I do not advocate for all the issues listed there, I do not like that  a company like Microsoft may profit from open source projects.

I continue to use GitHub because it offers the services I need for free.  I continue to monitor their terms of service.

Any use of this project's code by GitHub Copilot, past or present, is done  without our permission.  We do not consent to GitHub's use of this project's  code in Copilot.
