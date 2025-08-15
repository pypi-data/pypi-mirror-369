# Contributing

Contributions are welcome, and they are greatly appreciated! Every little bit helps, and credit will always be given.

You can contribute in many ways:

## Types of Contributions

### Report Bugs

Report bugs at https://github.com/audreyfeldroy/air_convert/issues.

If you are reporting a bug, please include:

- Your operating system name and version.
- Any details about your local setup that might be helpful in troubleshooting.
- Detailed steps to reproduce the bug.

### Fix Bugs

Look through the GitHub issues for bugs. Anything tagged with "bug" and "help wanted" is open to whoever wants to implement it.

### Implement Features

Look through the GitHub issues for features. Anything tagged with "enhancement" and "help wanted" is open to whoever wants to implement it.

### Write Documentation

air-convert could always use more documentation, whether as part of the official docs, in docstrings, or even on the web in blog posts, articles, and such.

### Submit Feedback

The best way to send feedback is to file an issue at https://github.com/audreyfeldroy/air_convert/issues.

If you are proposing a feature:

- Explain in detail how it would work.
- Keep the scope as narrow as possible, to make it easier to implement.
- Remember that this is a volunteer-driven project, and that contributions are welcome :)

## Get Started!

Ready to contribute? Here's how to set up `air_convert` for local development.

1. Fork the `air_convert` repo on GitHub.
2. Clone your fork locally:

   ```sh
   git clone git@github.com:your_name_here/air_convert.git
   ```

3. Install your local copy into a virtualenv. Assuming you have uv installed, this is how you set up your fork for local development:

   ```sh
   cd air_convert
   uv sync --extra dev
   ```

4. Create a branch for local development:

   ```sh
   git checkout -b name-of-your-bugfix-or-feature
   ```

   Now you can make your changes locally.

5. When you're done making changes, check that your changes pass flake8 and the tests, including testing other Python versions:

   ```sh
   just test   
   just qa
   # Or
   just testall
   ```

6. Commit your changes and push your branch to GitHub:

   ```sh
   git add .
   git commit -m "Your detailed description of your changes."
   git push origin name-of-your-bugfix-or-feature
   ```

7. Submit a pull request through the GitHub website.

## Pull Request Guidelines

Before you submit a pull request, check that it meets these guidelines:

1. The pull request should include tests.
2. If the pull request adds functionality, the docs should be updated. Put your new functionality into a function with a docstring, and add the feature to the list in README.md.
3. The pull request should work for Python 3.12 and 3.13. Tests run in GitHub Actions on every pull request to the main branch, make sure that the tests pass for all supported Python versions.

## Tips

To run a subset of tests:

```sh
just test tests.test_air_convert
```

## Deploying

A reminder for the maintainers on how to deploy to pypi. Make sure all changes are committed and merged. Then:

1. Update the version in `pyproject.toml`
2. Run `uv sync` to update the lockfile:

```sh
uv sync
```

3. Run a build test:

```sh
just build
```

4. Commit the changes

```sh
git commit -am 'Release vX.X.X'
```

5. Tag the current branch and push it up to github with this command:

```sh
just tags
```

6. If GitHub Action to deploy to PyPI isn't set up, use this command where `UV_PUBLISH_TOKEN` is your PyPI token:

```sh
uv publish -t $UV_PUBLISH_TOKEN
```

7. Once this is done, you can use the GitHub web interface to turn the tag into a formal release.

You can set up a [GitHub Actions workflow](https://docs.github.com/en/actions/use-cases-and-examples/building-and-testing/building-and-testing-python#publishing-to-pypi) to automatically deploy your package to PyPI when you push a new tag.

## Code of Conduct

Please note that this project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.
