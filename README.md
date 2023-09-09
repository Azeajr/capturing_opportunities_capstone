# Capturing Opportunities Capstone Project

<!-- PROJECT SHIELDS -->
<!--
*** I'm using markdown "reference style" links for readability.
*** Reference links are enclosed in brackets [ ] instead of parentheses ( ).
*** See the bottom of this document for the declaration of the reference variables
*** for contributors-url, forks-url, etc. This is an optional, concise syntax you may use.
*** https://www.markdownguide.org/basic-syntax/#reference-style-links
-->

[![Contributors][contributors-shield]][contributors-url]
[![Forks][forks-shield]][forks-url]
[![Stargazers][stars-shield]][stars-url]
[![Issues][issues-shield]][issues-url]
[![MIT License][license-shield]][license-url]
[![LinkedIn][linkedin-shield]][linkedin-url]

<!-- PROJECT LOGO -->
![Tux, the Linux mascot](/assets/images/tux.png)
### Capturing Opportunities: AI-Driven Photo Curation for Wildlife Photographer

#### Rationale:
Wildlife photographers may take thousands of photos in a given expedition, over many outings in a given time period, which can add up to tens of thousands of photos. They then have to scan through these images manually to remove those that were blurry or where the subject matter might not be oriented in a good position, etc. Using an ML model, we can complete this task and save the photographer days of work.

Although this time saving is reason enough to use ML, one more value proposition about applying ML in this domain excites me. Wildlife photographers also monetize their photos. Some photos generate a lot of income, while others do not. I wanted to use ML to help photographers identify more of these valuable photos that the photographer may have overlooked. In a set of 10,000 photos, a photographer may have chosen 100 photos that will be sold on their website. A model could be trained with these 100 photos to select other photos in this larger set of 10,000 to find other photos that may have been overlooked. This could be a huge value add for the photographer.

#### Objective:
To develop a web application that employs AI to effectively assist wildlife photographers in curating their photo collections. The application will employ a pre-trained image recognition model and use transfer learning to further train the model on a smaller set of images the user selects. Once this training is complete, the model is given a large set of photos to group. The expected output will be photos in the large set, which the model thinks can also be grouped with the smaller training set. This output represents photos that are also valuable. The goal is to make this happen in the context of a web app with minimal latency.

[![Explore the docs][product-screenshot]](https://github.com/Azeajr/capturing_opportunities_capstone)
[![View Demo][product-screenshot]](https://github.com/Azeajr/capturing_opportunities_capstone)
[![Report Bug][product-screenshot]](https://github.com/Azeajr/capturing_opportunities_capstone/issues)
[![Request Feature][product-screenshot]](https://github.com/Azeajr/capturing_opportunities_capstone/issues)


<details>
<summary>Table of Contents</summary>

- [Capturing Opportunities Capstone Project](#capturing-opportunities-capstone-project)
    - [Capturing Opportunities: AI-Driven Photo Curation for Wildlife Photographer](#capturing-opportunities-ai-driven-photo-curation-for-wildlife-photographer)
      - [Rationale:](#rationale)
      - [Objective:](#objective)
  - [About The Project](#about-the-project)
    - [Built With](#built-with)
  - [Getting Started](#getting-started)
    - [Prerequisites](#prerequisites)
    - [Installation](#installation)
  - [Usage](#usage)
  - [Roadmap](#roadmap)
  - [License](#license)
  - [Contributors](#contributors)
  - [Acknowledgments](#acknowledgments)
</details>

<!-- ABOUT THE PROJECT -->

## About The Project

[![Product Name Screen Shot][product-screenshot]](https://example.com)
Monorepo for the Capturing Opportunities Capstone Project

- flask_app
  - Flask version of the app
- svelte_app
  - Svelte version of the app

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

- [![Python][Python.org]][Python-url]
- [![Flask][Flask.palletsprojects]][Flask-url]
- [![Svelte][Svelte.dev]][Svelte-url]
- [![Rust][Rust.com]][Rust-url]
- [![Tensorflow][Tensorflow.org]][Tensorflow-url]
<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Getting Started

This is an example of how you may give instructions on setting up your project locally.
To get a local copy up and running follow these simple example steps.

### Prerequisites

### Installation

Svelte App

```bash
cd svelte_app
pnpm i
pnpm run dev -- --open
```

Flask App

```bash
cd flask_app
poetry install
poetry run flask run
```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- USAGE EXAMPLES -->

## Usage

Use this space to show useful examples of how a project can be used. Additional screenshots, code examples and demos work well in this space. You may also link to more resources.

_For more examples, please refer to the [Documentation](https://example.com)_

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- ROADMAP -->

## Roadmap

- [ ] Re-trainable ML Model
- [ ] Flask App with ML Model (prototype)
- [ ] Rust library for ML Model
- [ ] Svelte App with ML Model
  - [ ] Employing the Rust library

See the [open issues](https://github.com/Azeajr/capturing_opportunities_capstone/issues) for a full list of proposed features (and known issues).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->

## License

Distributed under the MIT License. See `LICENSE.txt` for more information.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

## Contributors
* [Donna Nguyen](https://github.com/donnahn87)
* [Antonio Zea Jr](https://github.com/Azeajr)


## Acknowledgments

- []()
- []()
- []()

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MARKDOWN LINKS & IMAGES -->
<!-- https://www.markdownguide.org/basic-syntax/#reference-style-links -->

[contributors-shield]: https://img.shields.io/github/contributors/Azeajr/capturing_opportunities_capstone.svg?style=for-the-badge
[contributors-url]: https://github.com/Azeajr/capturing_opportunities_capstone/graphs/contributors
[forks-shield]: https://img.shields.io/github/forks/Azeajr/capturing_opportunities_capstone.svg?style=for-the-badge
[forks-url]: https://github.com/Azeajr/capturing_opportunities_capstone/network/members
[stars-shield]: https://img.shields.io/github/stars/Azeajr/capturing_opportunities_capstone.svg?style=for-the-badge
[stars-url]: https://github.com/Azeajr/capturing_opportunities_capstone/stargazers
[issues-shield]: https://img.shields.io/github/issues/Azeajr/capturing_opportunities_capstone.svg?style=for-the-badge
[issues-url]: https://github.com/Azeajr/capturing_opportunities_capstone/issues
[license-shield]: https://img.shields.io/github/license/Azeajr/capturing_opportunities_capstone.svg?style=for-the-badge
[license-url]: https://github.com/Azeajr/capturing_opportunities_capstone/blob/master/LICENSE.txt
[linkedin-shield]: https://img.shields.io/badge/-LinkedIn-black.svg?style=for-the-badge&logo=linkedin&colorB=555
[linkedin-url]: https://linkedin.com/in/linkedin_username
[product-screenshot]: images/screenshot.png
[Python.org]: https://img.shields.io/badge/python-%2314354C.svg?style=for-the-badge&logo=python&logoColor=white
[Python-url]: https://www.python.org/
[Flask.palletsprojects]: https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white
[Flask-url]: https://flask.palletsprojects.com/en/2.0.x/
[Svelte.dev]: https://img.shields.io/badge/Svelte-4A4A55?style=for-the-badge&logo=svelte&logoColor=FF3E00
[Svelte-url]: https://svelte.dev/
[Rust.com]: https://img.shields.io/badge/rust-%23000000.svg?style=for-the-badge&logo=rust&logoColor=white
[Rust-url]: https://www.rust-lang.org/
[Tensorflow.org]: https://img.shields.io/badge/TensorFlow-FF6F00?style=for-the-badge&logo=TensorFlow&logoColor=white
[Tensorflow-url]: https://www.tensorflow.org/
