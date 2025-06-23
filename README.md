
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
<!--[![LinkedIn][linkedin-shield]][linkedin-url]-->



<!-- PROJECT LOGO -->
<br />
<p align="center">
  <h3 align="center">pydreo-cloud</h3>

  <p align="center">
    Library for connecting to dreo cloud.
    <br />
    <br />
    <a href="https://github.com/dreo-team/pydreo-cloud/issues">Report Bug</a>
    ·
    <a href="https://github.com/dreo-team/pydreo-cloud/issues">Request Feature</a>
  </p>
</p>


## About The Project

Simple implementation for logging in to your Dreo cloud account and fetch device information.


<!-- USAGE EXAMPLES -->
## Usage

How to get and use pydreo-cloud.

###  Getting it

To download pydreo-cloud, either fork this github repo or use Pypi via pip.
```sh
$ pip install pydreo-cloud
```

### Using it
You can use pydreo-cloud in your project.

#### In code:
As of right now there's not much you can do. You can login and get device info from Dreo cloud:
```Python
from pydreo-cloud.client import DreoClient

manage = DreoClient("USERNAME", "PASSWORD")
manage.login()

# get list of devices
devices = manage.get_devices()

# get status of devices
status = manage.get_status("DEVICESN")
```

<!-- LICENSE -->
## License

Distributed under the MIT License. See `LICENSE` for more information.



<!-- CONTACT -->
## Contact

Dreo Team: [developer@dreo.com](mailto:developer@dreo.com)

Project Link: [https://github.com/dreo-team/pydreo-cloud](https://github.com/dreo-team/pydreo-cloud)




<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/squachen/micloud.svg?style=flat-square
[contributors-url]: https://github.com/dreo-team/pydreo-cloud/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/Squachen/micloud.svg?style=flat-square
[forks-url]: https://github.com/dreo-team/pydreo-cloud/network/members
[stars-shield]: https://img.shields.io/github/stars/squachen/micloud.svg?style=flat-square
[stars-url]: https://github.com/dreo-team/pydreo-cloud/stargazers
[issues-shield]: https://img.shields.io/github/issues/squachen/micloud.svg?style=flat-square
[issues-url]: https://github.com/dreo-team/pydreo-cloud/issues
[license-shield]: https://img.shields.io/github/license/squachen/micloud.svg?style=flat-square
[license-url]: https://github.com/dreo-team/pydreo-cloud/blob/master/LICENSE.txt

