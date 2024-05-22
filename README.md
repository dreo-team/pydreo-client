
[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
<!--[![LinkedIn][linkedin-shield]][linkedin-url]-->



<!-- PROJECT LOGO -->
<br />
<p align="center">
  <h3 align="center">HsCloud</h3>

  <p align="center">
    Library for connecting to dreo cloud.
    <br />
    <br />
    <a href="https://github.com/dreo-team/hscloud/issues">Report Bug</a>
    ·
    <a href="https://github.com/dreo-team/hscloud/issues">Request Feature</a>
  </p>
</p>


## About The Project

Simple implementation for logging in to your Dreo cloud account and fetch device information.


<!-- USAGE EXAMPLES -->
## Usage

How to get and use hscloud.

###  Getting it

To download hscloud, either fork this github repo or use Pypi via pip.
```sh
$ pip install hscloud
```

### Using it
You can use hscloud in your project.

#### In code:
As of right now there's not much you can do. You can login and get device info from Dreo cloud:
```Python
from hscloud.hscloud import HsCloud

manage = HsCloud("USERNAME", "PASSWORD")
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

Dreo Team: [app@hesung.com](mailto:app@hesung.com)

Project Link: [https://github.com/dreo-team/hscloud](https://github.com/dreo-team/hscloud)




<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->
[contributors-shield]: https://img.shields.io/github/contributors/squachen/micloud.svg?style=flat-square
[contributors-url]: https://github.com/dreo-team/hscloud/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/Squachen/micloud.svg?style=flat-square
[forks-url]: https://github.com/dreo-team/hscloud/network/members
[stars-shield]: https://img.shields.io/github/stars/squachen/micloud.svg?style=flat-square
[stars-url]: https://github.com/dreo-team/hscloud/stargazers
[issues-shield]: https://img.shields.io/github/issues/squachen/micloud.svg?style=flat-square
[issues-url]: https://github.com/dreo-team/hscloud/issues
[license-shield]: https://img.shields.io/github/license/squachen/micloud.svg?style=flat-square
[license-url]: https://github.com/dreo-team/hscloud/blob/master/LICENSE.txt

