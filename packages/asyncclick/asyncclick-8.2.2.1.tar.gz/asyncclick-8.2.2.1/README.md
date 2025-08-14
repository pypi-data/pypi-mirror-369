<div align="center"><img src="https://raw.githubusercontent.com/pallets/click/refs/heads/stable/docs/_static/click-name.svg" alt="" height="150"></div>

# AsyncClick

[AsyncClick][] is a fork of Click that works well with [anyio][], [Trio][], or [asyncio][].

[anyio]: https://anyio.readthedocs.io/en/stable/
[Trio]: https://trio.readthedocs.io/en/stable/
[asyncio]: https://docs.python.org/3/library/asyncio.html
[AsyncClick]: https://github.com/python-trio/asyncclick/

# Click

Click is a Python package for creating beautiful command line interfaces
in a composable way with as little code as necessary. It's the "Command
Line Interface Creation Kit". It's highly configurable but comes with
sensible defaults out of the box.

It aims to make the process of writing command line tools quick and fun
while also preventing any frustration caused by the inability to
implement an intended CLI API.

AsyncClick in four points:

-   Arbitrary nesting of commands
-   Automatic help page generation
-   Supports lazy loading of subcommands at runtime
-   Seamlessly use async-enabled command and subcommand handlers


## A Simple Example

```python
import asyncclick as click
import anyio

@click.command()
@click.option("--count", default=1, help="Number of greetings.")
@click.option("--name", prompt="Your name", help="The person to greet.")
async def hello(count, name):
    """Simple program that greets NAME for a total of COUNT times."""
    for x in range(count):
        if x:
            await anyio.sleep(0.1)
        click.echo(f"Hello, {name}!")

if __name__ == '__main__':
    hello()
```

```
$ python hello.py --count=3
Your name: Click
Hello, Click!
Hello, Click!
Hello, Click!
```

Compared to the original [Click][], you'll note that AsyncClick supports
optional(!) sprinkling of `async`/`await` keywords wherever your code needs
them.

In the interest of not diverging from Click more than absolutely necessary,
many examples have not been touched.


[Click]: https://palletsprojects.com/p/click/

## Donate

The Pallets organization develops and supports Click and other popular
packages. In order to grow the community of contributors and users, and
allow the maintainers to devote more time to the projects, [please
donate today][].

[please donate today]: https://palletsprojects.com/donate

The AsyncClick fork is maintained by Matthias Urlichs <matthias@urlichs.de>.
It's not a lot of work, so if you'd like to motivate me, donate to the
charity of your choice and tell me that you've done so. ;-)

## Contributing

See our [detailed contributing documentation][contrib] for many ways to
contribute, including reporting issues, requesting features, asking or answering
questions, and making PRs.

[contrib]: https://palletsprojects.com/contributing/
