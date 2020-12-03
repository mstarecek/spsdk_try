Overview
========

Secure Provisioning SDK (SPSDK) is unified, reliable and easy to use SW library working across NXP MCU and MPU portfolio providing strong 
foundation from quick customer prototyping up to production deployment. Is following the philosophy: **code less but do more**. 

<p align="center">
  <img src="_static/images/spsdk.png" alt="SPSDK Concept"/>
</p>

**SPSDK Modules:**

- **Crypto** - Support for key's and certificate's operations
- **DAT** - Covering functionality of `debug authentication` tool
- **Image** - Covering functionality of `srktool`, `dcdgen`, `mkimage` and other similar tools
- **MBoot** - Covering functionality of `blhost` tool
- **PFR** - Support for configuration of Protected Flash Region areas (CMPA, CFPA)
- **SBFile** - Covering functionality of `elftosb` tool
- **SDP** - Covering functionality of `sdphost` tool


Installation
============

Installation directly from master branch [bitbucket.sw.nxp.com](https://bitbucket.sw.nxp.com/projects/SPSDK/repos/spsdk/browse):

```bash
pip install -U https://bitbucket.sw.nxp.com/rest/api/latest/projects/SPSDK/repos/spsdk/archive?format=zip
```

If you will be asked for credentials, use your NXP login and password:

```text
User for bitbucket.sw.nxp.com: nxa...
Password: ******
```

In case of development, install SPSDK from sources:

```bash
git clone ssh://git@bitbucket.sw.nxp.com/spsdk/spsdk.git
cd spsdk
pip install -r requirements-develop.txt
pip install -U -e .
```

Note: If you use pip version 20.3, please downgrade it to 20.2.4, because of new resolver functionality.
 
 
Dependencies
============

SPSDK requires [Python](https://www.python.org) >3.5 and <3.9 interpreter, old version 2.x is not supported !

The core dependencies are included in requirements.txt file. 

The dependencies for the development and testing are included in requirements-develop.txt.